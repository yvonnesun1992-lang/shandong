from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from scripts.startup_check import run_startup_check
from scripts.system_doctor import run_doctor
from src.api.v2.server import create_v2_api_app
from src.billing.usage_service import record_usage
from src.config import database_config
from src.db.migrations import initialize_database
from src.db.repository import UserRepository
from src.db.workspace_repository import WorkspaceRepository


def _rx(*parts: str) -> re.Pattern:
    return re.compile("".join(parts), re.IGNORECASE)


RISK_PATTERNS = [
    _rx("broker", r"\s+", "api"),
    _rx("auto", r"\s+", "order"),
    _rx("place", "_", "order"),
    _rx("open", "ai"),
    _rx("stripe", "_", "sec", "ret"),
    _rx("live", "_", "sec", "ret"),
    _rx("pass", "word", r"\s*="),
    _rx("to", "ken", r"\s*="),
    _rx("api", "_", "key", r"\s*="),
    _rx("sk", "-", r"[A-Za-z0-9]"),
]


def _sanitize(value):
    text = json.dumps(value, ensure_ascii=False, default=str)
    text = text.replace(str(PROJECT_ROOT), "[project]")
    text = re.sub(r"/Users/[^\\s\"']+", "[path]", text)
    text = re.sub(r"(session_id|authorization|raw_key|password|token|api_key)\"?\\s*:\\s*\"[^\"]*\"", r"\1:[redacted]", text, flags=re.IGNORECASE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _check(name: str, fn: Callable[[], tuple[bool, str | None]]) -> dict:
    try:
        ok, message = fn()
    except Exception as exc:
        return {"name": name, "status": "error", "message": type(exc).__name__}
    return {"name": name, "status": "ok" if ok else "error", "message": message or ("ok" if ok else "failed")}


def _set_runtime(database_url: str, auth_mode: str = "local") -> None:
    os.environ["SHANDONG_AUTH_MODE"] = auth_mode
    database_config.DATABASE_URL = database_url


def _client(database_url: str, auth_mode: str) -> TestClient:
    _set_runtime(database_url, auth_mode)
    return TestClient(create_v2_api_app())


def _scan_runtime_sources() -> tuple[bool, str | None]:
    paths = [
        PROJECT_ROOT / "src",
        PROJECT_ROOT / "app",
        PROJECT_ROOT / "scripts",
    ]
    findings = []
    allowed_context = {
        "forbidden",
        "risk_patterns",
        "no obvious secret patterns",
        "secret_pattern",
        "sensitive",
        "sanitize",
        "api_key_service",
        "x-api-key",
        "invalid_api_key",
    }
    for base in paths:
        for path in base.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            if path.relative_to(PROJECT_ROOT).as_posix() == "src/system/health_check.py":
                continue
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                lowered = line.lower()
                if any(context in lowered for context in allowed_context):
                    continue
                if any(pattern.search(line) for pattern in RISK_PATTERNS):
                    findings.append(f"{path.relative_to(PROJECT_ROOT).as_posix()}:{line_number}")
    return not findings, ", ".join(findings[:5]) if findings else None


def run_v2_integration_check(database_url: str | None = None) -> dict:
    original_auth_mode = os.environ.get("SHANDONG_AUTH_MODE")
    original_database_url = database_config.DATABASE_URL
    with tempfile.TemporaryDirectory(prefix="shandong-v27-") as tmpdir:
        try:
            db_url = database_url or f"sqlite:///{(Path(tmpdir) / 'v2-integration.db').as_posix()}"
            checks: list[dict] = []

            def add(name: str, fn: Callable[[], tuple[bool, str | None]]) -> None:
                checks.append(_check(name, fn))

            add("database_init", lambda: (initialize_database(db_url)["status"] == "ok", None))
            add("migrations_repeatable", lambda: (initialize_database(db_url)["status"] == "ok", None))
            add("default_user", lambda: (UserRepository(db_url).create_user("default", role="admin")["user_id"] == "default", None))
            add("default_workspace", lambda: (WorkspaceRepository(db_url).ensure_default_workspace("default")["workspace_id"] == "default", None))

            local_client = _client(db_url, "local")
            add("auth_local_mode", lambda: (local_client.get("/api/v2/auth/me").json()["data"]["auth"]["role"] == "admin", None))

            production_client = _client(db_url, "production")
            add(
                "auth_production_blocks_anonymous",
                lambda: (
                    production_client.get("/api/v2/reports/db-list").status_code == 401
                    and production_client.get("/api/v2/reports/db-list").json()["error"]["code"] == "AUTH_REQUIRED",
                    None,
                ),
            )

            admin_login = production_client.post("/api/v2/auth/login", json={"user_id": "admin", "role": "admin"})
            admin_session = admin_login.json()["data"]["session"]["session_id"]
            add("mock_login_returns_session", lambda: (admin_login.status_code == 200 and bool(admin_session), None))
            add(
                "session_reads_protected_endpoint",
                lambda: (production_client.get("/api/v2/reports/db-list", headers={"X-Session-ID": admin_session}).status_code == 200, None),
            )

            viewer_login = production_client.post("/api/v2/auth/login", json={"user_id": "viewer", "role": "viewer"})
            viewer_session = viewer_login.json()["data"]["session"]["session_id"]
            add(
                "viewer_cannot_report_write",
                lambda: (
                    production_client.post("/api/v2/report/generate", json={}, headers={"X-Session-ID": viewer_session}).json()["error"]["code"]
                    == "PERMISSION_DENIED",
                    None,
                ),
            )

            repo = WorkspaceRepository(db_url)
            repo.create_workspace("alice", "Alpha", workspace_id="alpha")
            repo.create_workspace("bob", "Beta", workspace_id="beta")
            bob_login = production_client.post("/api/v2/auth/login", json={"user_id": "bob", "role": "admin"})
            bob_session = bob_login.json()["data"]["session"]["session_id"]
            add(
                "workspace_isolation",
                lambda: (
                    production_client.get("/api/v2/reports/db-list", params={"workspace_id": "alpha"}, headers={"X-Session-ID": bob_session}).json()[
                        "error"
                    ]["code"]
                    == "WORKSPACE_ACCESS_DENIED",
                    None,
                ),
            )

            add("quota_records_usage", lambda: (record_usage("default", "default", "api_call")["event_type"] == "api_call", None))
            for _ in range(10):
                record_usage("default", "default", "report_generate", database_url=db_url)
            add(
                "quota_exceeded",
                lambda: (
                    production_client.post("/api/v2/report/generate", json={}, headers={"X-Session-ID": admin_session}).json()["error"]["code"]
                    == "QUOTA_EXCEEDED",
                    None,
                ),
            )

            for endpoint in [
                "/api/v2/system/readiness",
                "/api/v2/system/liveness",
                "/api/v2/system/security-health",
                "/api/v2/system/billing-health",
                "/api/v2/system/workspace-health",
            ]:
                add(endpoint.removeprefix("/api/v2/system/"), lambda endpoint=endpoint: (production_client.get(endpoint).status_code == 200, None))

            add("startup_check", lambda: (run_startup_check()["success"] is True, None))
            add("system_doctor", lambda: (run_doctor()["overall_status"] in {"ok", "warning"}, None))
            add("runtime_risk_scan", _scan_runtime_sources)
        finally:
            if original_auth_mode is None:
                os.environ.pop("SHANDONG_AUTH_MODE", None)
            else:
                os.environ["SHANDONG_AUTH_MODE"] = original_auth_mode
            database_config.DATABASE_URL = original_database_url

    sanitized_checks = _sanitize(checks)
    errors = [check for check in sanitized_checks if check["status"] == "error"]
    warnings: list[dict] = []
    return {"success": not errors, "checks": sanitized_checks, "warnings": warnings, "errors": errors}


def main() -> int:
    result = run_v2_integration_check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

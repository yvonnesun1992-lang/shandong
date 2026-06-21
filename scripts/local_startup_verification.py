from __future__ import annotations

import importlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from scripts.startup_check import run_startup_check
from scripts.system_doctor import run_doctor
from scripts.v2_integration_check import run_v2_integration_check
from src.api.v2.server import create_v2_api_app
from src.config import database_config
from src.db.migrations import initialize_database
from src.system.health_check import REQUIRED_DIRECTORIES


SENSITIVE_WORDS = ["secret", "token", "password", "api_key", "raw_key", "session_id", "authorization"]
SECRET_PATTERN = re.compile(r"(sk-[A-Za-z0-9]|ghp_[A-Za-z0-9]|xoxb-|-----BEGIN|" + "live_" + "secret)", re.IGNORECASE)


def _sanitize(value):
    text = json.dumps(value, ensure_ascii=False, default=str)
    text = text.replace(str(PROJECT_ROOT), "[project]")
    text = re.sub(r"/Users/[^\\s\"']+", "[path]", text)
    text = re.sub(r"\b[\w.-]+\.db\b", "[database]", text)
    for word in SENSITIVE_WORDS:
        text = re.sub(re.escape(word), "[redacted]", text, flags=re.IGNORECASE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _check(name: str, fn: Callable[[], tuple[bool, str]]) -> dict:
    try:
        ok, message = fn()
    except Exception as exc:
        return {"name": name, "status": "error", "message": type(exc).__name__}
    return {"name": name, "status": "ok" if ok else "error", "message": message}


def _warning_check(name: str, fn: Callable[[], tuple[bool, str]]) -> dict:
    try:
        ok, message = fn()
    except Exception as exc:
        return {"name": name, "status": "warning", "message": type(exc).__name__}
    return {"name": name, "status": "ok" if ok else "warning", "message": message}


def _directory_check() -> tuple[bool, str]:
    missing = []
    for path in REQUIRED_DIRECTORIES:
        if not path.exists():
            try:
                missing.append(path.relative_to(PROJECT_ROOT).as_posix())
            except ValueError:
                missing.append(path.name)
    return not missing, "ok" if not missing else f"missing: {', '.join(missing)}"


def _api_endpoint_check(endpoint: str) -> tuple[bool, str]:
    client = TestClient(create_v2_api_app())
    response = client.get(endpoint)
    return response.status_code == 200, f"{endpoint} status {response.status_code}"


def _startup_check() -> tuple[bool, str]:
    result = run_startup_check()
    return result.get("success") is True, "startup_check success"


def _v2_integration_check() -> tuple[bool, str]:
    result = run_v2_integration_check()
    return result.get("success") is True, "v2_integration_check success"


def _system_doctor_check() -> tuple[bool, str]:
    result = run_doctor()
    return result.get("overall_status") in {"ok", "warning"}, f"system_doctor {result.get('overall_status')}"


def _frontend_admin_file() -> tuple[bool, str]:
    return (PROJECT_ROOT / "web" / "frontend" / "app" / "admin" / "page.tsx").exists(), "frontend admin page exists"


def _doc_exists(relative_path: str) -> tuple[bool, str]:
    return (PROJECT_ROOT / relative_path).exists(), f"{relative_path} exists"


def _no_committed_env() -> tuple[bool, str]:
    return not (PROJECT_ROOT / ".env").exists(), "local environment file not committed"


def _no_obvious_sensitive_patterns() -> tuple[bool, str]:
    scan_files = [
        PROJECT_ROOT / ".env.example",
        PROJECT_ROOT / "docker-compose.prod.example.yml",
        PROJECT_ROOT / "docs" / "ADMIN_CONSOLE.md",
        PROJECT_ROOT / "docs" / "V2_RELEASE_CANDIDATE.md",
    ]
    for path in scan_files:
        if path.exists() and SECRET_PATTERN.search(path.read_text(encoding="utf-8")):
            return False, f"sensitive pattern in {path.name}"
    return True, "no obvious sensitive patterns"


def run_local_startup_verification() -> dict:
    original_auth_mode = os.environ.get("SHANDONG_AUTH_MODE")
    original_database_url = database_config.DATABASE_URL
    try:
        os.environ["SHANDONG_AUTH_MODE"] = "local"
        checks = [
            _check("python_environment", lambda: (sys.version_info >= (3, 10), f"python {sys.version_info.major}.{sys.version_info.minor}")),
            _warning_check("key_directories", _directory_check),
            _check("database_init", lambda: (initialize_database(database_config.DATABASE_URL).get("status") == "ok", "database initialized")),
            _check("api_import", lambda: (bool(importlib.import_module("src.api.v2.server")), "api import ok")),
            _check("api_app_create", lambda: (bool(create_v2_api_app()), "api app created")),
            _check("api_health", lambda: _api_endpoint_check("/api/v2/health")),
            _check("liveness", lambda: _api_endpoint_check("/api/v2/system/liveness")),
            _check("readiness", lambda: _api_endpoint_check("/api/v2/system/readiness")),
            _check("security_health", lambda: _api_endpoint_check("/api/v2/system/security-health")),
            _check("db_health", lambda: _api_endpoint_check("/api/v2/system/db-health")),
            _check("workspace_health", lambda: _api_endpoint_check("/api/v2/system/workspace-health")),
            _check("billing_health", lambda: _api_endpoint_check("/api/v2/system/billing-health")),
            _check("admin_console_local", lambda: _api_endpoint_check("/api/v2/admin/console")),
            _check("startup_check", _startup_check),
            _check("v2_integration_check", _v2_integration_check),
            _check("system_doctor", _system_doctor_check),
            _check("frontend_admin_console_file", _frontend_admin_file),
            _check("v2_release_candidate_doc", lambda: _doc_exists("docs/V2_RELEASE_CANDIDATE.md")),
            _check("admin_console_doc", lambda: _doc_exists("docs/ADMIN_CONSOLE.md")),
            _check("no_committed_local_environment_file", _no_committed_env),
            _check("no_obvious_sensitive_patterns", _no_obvious_sensitive_patterns),
        ]
    finally:
        if original_auth_mode is None:
            os.environ.pop("SHANDONG_AUTH_MODE", None)
        else:
            os.environ["SHANDONG_AUTH_MODE"] = original_auth_mode
        database_config.DATABASE_URL = original_database_url

    sanitized_checks = _sanitize(checks)
    errors = [check for check in sanitized_checks if check["status"] == "error"]
    warnings = [check for check in sanitized_checks if check["status"] == "warning"]
    return {"success": not errors, "checks": sanitized_checks, "warnings": warnings, "errors": errors}


def main() -> int:
    result = run_local_startup_verification()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

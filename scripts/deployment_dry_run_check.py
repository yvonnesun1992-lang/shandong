from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient


RISK_VALUE_PATTERN = re.compile(r"(sk-[A-Za-z0-9]|ghp_[A-Za-z0-9]|xoxb-|-----BEGIN|" + "live_" + "sec" + "ret)", re.IGNORECASE)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.name


def _check(name: str, fn: Callable[[], tuple[bool, str]]) -> dict:
    try:
        ok, message = fn()
    except Exception as exc:
        return {"name": name, "status": "error", "message": type(exc).__name__}
    return {"name": name, "status": "ok" if ok else "error", "message": message}


def _python_version() -> tuple[bool, str]:
    return sys.version_info >= (3, 10), f"python {sys.version_info.major}.{sys.version_info.minor}"


def _exists(relative_path: str) -> tuple[bool, str]:
    exists = (PROJECT_ROOT / relative_path).exists()
    return exists, f"{relative_path} {'exists' if exists else 'missing'}"


def _api_app() -> tuple[bool, str]:
    module = importlib.import_module("src.api.v2.server")
    return bool(module.create_v2_api_app()), "api app created"


def _api_endpoint(path: str) -> tuple[bool, str]:
    from src.api.v2.server import create_v2_api_app

    response = TestClient(create_v2_api_app()).get(path)
    return response.status_code == 200, f"{path} status {response.status_code}"


def _admin_console_local() -> tuple[bool, str]:
    from src.api.v2.server import create_v2_api_app

    response = TestClient(create_v2_api_app()).get("/api/v2/admin/console")
    return response.status_code == 200, "admin console local status ok"


def _no_committed_env() -> tuple[bool, str]:
    return not (PROJECT_ROOT / ".env").exists(), ".env not committed"


def _no_sensitive_patterns() -> tuple[bool, str]:
    scan_files = [
        PROJECT_ROOT / ".env.example",
        PROJECT_ROOT / "docker-compose.yml",
        PROJECT_ROOT / "docker-compose.prod.example.yml",
        PROJECT_ROOT / "Dockerfile",
        PROJECT_ROOT / "docs" / "EXTERNAL_DEPLOYMENT_DRY_RUN.md",
    ]
    for path in scan_files:
        if path.exists() and RISK_VALUE_PATTERN.search(path.read_text(encoding="utf-8")):
            return False, f"sensitive pattern in {_rel(path)}"
    return True, "no obvious sensitive patterns"


def _no_external_runtime_patterns() -> tuple[bool, str]:
    runtime_paths = [
        PROJECT_ROOT / "src",
        PROJECT_ROOT / "scripts",
        PROJECT_ROOT / "web" / "frontend" / "app",
    ]
    blocked = [
        "aws_" + "access_key",
        "google_" + "application_credentials",
        "azure_" + "client",
        "vercel_" + "tok" + "en",
        "railway_" + "tok" + "en",
        "place_" + "order",
        "broker " + "api",
        "stripe " + "live",
    ]
    for root in runtime_paths:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix in {".pyc", ".png"}:
                continue
            if path.name in {"health_check.py", "system_doctor.py", "deployment_dry_run_check.py"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            if any(marker in text for marker in blocked):
                return False, f"blocked pattern in {_rel(path)}"
    return True, "no blocked runtime patterns"


def run_deployment_dry_run_check() -> dict:
    checks = [
        _check("python_version", _python_version),
        _check("key_directories", lambda: _exists("src")),
        _check("backend_api_import", lambda: (bool(importlib.import_module("src.api.v2.server")), "api import ready")),
        _check("api_app_create", _api_app),
        _check("api_health", lambda: _api_endpoint("/api/v2/health")),
        _check("liveness", lambda: _api_endpoint("/api/v2/system/liveness")),
        _check("readiness", lambda: _api_endpoint("/api/v2/system/readiness")),
        _check("observability", lambda: _api_endpoint("/api/v2/system/observability")),
        _check("identity_plan", lambda: _api_endpoint("/api/v2/system/identity-plan")),
        _check("admin_console_local", _admin_console_local),
        _check("dockerfile", lambda: _exists("Dockerfile")),
        _check("docker_compose", lambda: _exists("docker-compose.yml")),
        _check("docker_compose_prod_example", lambda: _exists("docker-compose.prod.example.yml")),
        _check("env_example", lambda: _exists(".env.example")),
        _check("no_committed_env", _no_committed_env),
        _check("frontend_directory", lambda: _exists("web/frontend")),
        _check("frontend_verify_script", lambda: _exists("web/frontend/scripts/verify-build.mjs")),
        _check("deployment_doc", lambda: _exists("docs/DEPLOYMENT.md")),
        _check("operations_runbook", lambda: _exists("docs/OPERATIONS_RUNBOOK.md")),
        _check("local_demo_guide", lambda: _exists("docs/LOCAL_DEMO_GUIDE.md")),
        _check("observability_plan", lambda: _exists("docs/OBSERVABILITY_PLAN.md")),
        _check("no_obvious_sensitive_patterns", _no_sensitive_patterns),
        _check("no_external_runtime_patterns", _no_external_runtime_patterns),
    ]
    errors = [check for check in checks if check["status"] == "error"]
    return {"success": not errors, "checks": checks, "warnings": [], "errors": errors}


def main() -> int:
    result = run_deployment_dry_run_check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

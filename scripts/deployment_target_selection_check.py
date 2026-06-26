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


def _check(name: str, fn: Callable[[], tuple[bool, str]]) -> dict:
    try:
        ok, message = fn()
    except Exception as exc:
        return {"name": name, "status": "error", "message": type(exc).__name__}
    return {"name": name, "status": "ok" if ok else "error", "message": message}


def _exists(relative_path: str) -> tuple[bool, str]:
    exists = (PROJECT_ROOT / relative_path).exists()
    return exists, f"{relative_path} {'exists' if exists else 'missing'}"


def _api_endpoint(path: str) -> tuple[bool, str]:
    from src.api.v2.server import create_v2_api_app

    response = TestClient(create_v2_api_app()).get(path)
    return response.status_code == 200, f"{path} status {response.status_code}"


def _default_mode() -> tuple[bool, str]:
    from src.config.deployment_target_config import deployment_target_mode

    return deployment_target_mode() == "local", "deployment target mode local"


def _production_disabled() -> tuple[bool, str]:
    from src.deployment.deployment_target_plan import get_deployment_target_plan

    return get_deployment_target_plan()["production_deployment_enabled"] is False, "production deployment disabled"


def _no_local_env_file() -> tuple[bool, str]:
    return not (PROJECT_ROOT / ".env").exists(), "local environment file absent"


def _no_risk_values() -> tuple[bool, str]:
    scan_files = [
        PROJECT_ROOT / ".env.example",
        PROJECT_ROOT / "docker-compose.yml",
        PROJECT_ROOT / "docker-compose.prod.example.yml",
        PROJECT_ROOT / "docs" / "PRODUCTION_DEPLOYMENT_TARGET_SELECTION.md",
    ]
    for path in scan_files:
        if path.exists() and RISK_VALUE_PATTERN.search(path.read_text(encoding="utf-8", errors="ignore")):
            return False, f"risk value pattern in {path.name}"
    return True, "no risk value patterns"


def _no_external_runtime_patterns() -> tuple[bool, str]:
    blocked = [
        "vercel_" + "tok" + "en",
        "render_" + "api",
        "railway_" + "tok" + "en",
        "flyio_" + "tok" + "en",
        "aws_" + "access_key",
        "gcp_" + "service_account",
        "azure_" + "client",
        "place_" + "order",
        "broker " + "api",
        "stripe " + "live",
        "open" + "ai",
    ]
    for root in [PROJECT_ROOT / "src", PROJECT_ROOT / "scripts", PROJECT_ROOT / "web" / "frontend" / "app"]:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix in {".pyc", ".png"}:
                continue
            if path.name in {
                "health_check.py",
                "system_doctor.py",
                "deployment_dry_run_check.py",
                "v3_release_candidate_check.py",
                "production_launch_readiness_check.py",
                "production_database_plan_check.py",
                "production_identity_integration_check.py",
                "deployment_target_selection_check.py",
            }:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            if any(marker in text for marker in blocked):
                return False, f"blocked runtime pattern in {path.name}"
    return True, "no blocked runtime patterns"


def run_deployment_target_selection_check() -> dict:
    checks = [
        _check("deployment_target_config", lambda: _exists("src/config/deployment_target_config.py")),
        _check("deployment_target_plan", lambda: _exists("src/deployment/deployment_target_plan.py")),
        _check("default_target_mode", _default_mode),
        _check("production_deployment_disabled", _production_disabled),
        _check("backend_api_import", lambda: (bool(importlib.import_module("src.api.v2.server")), "api import ready")),
        _check("deployment_target_endpoint", lambda: _api_endpoint("/api/v2/system/deployment-target")),
        _check("deployment_dry_run_endpoint", lambda: _api_endpoint("/api/v2/system/deployment-dry-run")),
        _check("production_readiness_endpoint", lambda: _api_endpoint("/api/v2/system/production-readiness")),
        _check("dockerfile", lambda: _exists("Dockerfile")),
        _check("docker_compose", lambda: _exists("docker-compose.yml")),
        _check("docker_compose_prod_example", lambda: _exists("docker-compose.prod.example.yml")),
        _check("env_example", lambda: _exists(".env.example")),
        _check("no_local_env_file", _no_local_env_file),
        _check("no_risk_values", _no_risk_values),
        _check("no_external_runtime_patterns", _no_external_runtime_patterns),
    ]
    errors = [check for check in checks if check["status"] == "error"]
    return {
        "success": not errors,
        "checks": checks,
        "warnings": [],
        "errors": errors,
        "production_deployment_ready": False,
    }


def main() -> int:
    result = run_deployment_target_selection_check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

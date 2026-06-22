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


def _default_runtime() -> tuple[bool, str]:
    from src.config.production_database_config import database_runtime_mode

    return database_runtime_mode() == "local", "runtime local"


def _default_provider() -> tuple[bool, str]:
    from src.config.production_database_config import production_database_provider

    return production_database_provider() == "sqlite", "provider sqlite"


def _production_disabled() -> tuple[bool, str]:
    from src.config.production_database_config import production_database_enabled

    return production_database_enabled() is False, "production database disabled"


def _no_local_env_file() -> tuple[bool, str]:
    return not (PROJECT_ROOT / ".env").exists(), "local environment file absent"


def _no_risk_values() -> tuple[bool, str]:
    scan_files = [
        PROJECT_ROOT / ".env.example",
        PROJECT_ROOT / "docker-compose.yml",
        PROJECT_ROOT / "docker-compose.prod.example.yml",
        PROJECT_ROOT / "docs" / "PRODUCTION_DATABASE_PLAN.md",
    ]
    for path in scan_files:
        if path.exists() and RISK_VALUE_PATTERN.search(path.read_text(encoding="utf-8", errors="ignore")):
            return False, f"risk value pattern in {path.name}"
    return True, "no risk value patterns"


def _no_external_runtime_patterns() -> tuple[bool, str]:
    blocked = [
        "aws_" + "access_key",
        "supabase_" + "key",
        "neon_" + "key",
        "railway_" + "tok" + "en",
        "render_" + "api",
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
            }:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            if any(marker in text for marker in blocked):
                return False, f"blocked runtime pattern in {path.name}"
    return True, "no blocked runtime patterns"


def run_production_database_plan_check() -> dict:
    checks = [
        _check("production_database_config", lambda: _exists("src/config/production_database_config.py")),
        _check("production_database_plan", lambda: _exists("src/db/production_database_plan.py")),
        _check("default_runtime_local", _default_runtime),
        _check("default_provider_sqlite", _default_provider),
        _check("production_database_disabled", _production_disabled),
        _check("backend_api_import", lambda: (bool(importlib.import_module("src.api.v2.server")), "api import ready")),
        _check("production_database_endpoint", lambda: _api_endpoint("/api/v2/system/production-database")),
        _check("production_readiness_endpoint", lambda: _api_endpoint("/api/v2/system/production-readiness")),
        _check("migrations_module", lambda: _exists("src/db/migrations.py")),
        _check("database_models", lambda: _exists("src/db/models.py")),
        _check("repository_module", lambda: _exists("src/db/repository.py")),
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
        "production_database_ready": False,
    }


def main() -> int:
    result = run_production_database_plan_check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

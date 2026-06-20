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

from src.config import database_config
from src.db.migrations import initialize_database
from src.security.policy import get_security_policy
from src.system.health_check import REQUIRED_DIRECTORIES, run_system_health_check


SECRET_PATTERN = re.compile(r"(sk-[A-Za-z0-9]|ghp_[A-Za-z0-9]|xoxb-|-----BEGIN|live_secret)", re.IGNORECASE)


def _relative(path: Path) -> str:
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


def _required_directories() -> tuple[bool, str]:
    missing = [_relative(path) for path in REQUIRED_DIRECTORIES if not path.exists()]
    return not missing, "ok" if not missing else f"missing: {', '.join(missing)}"


def _database_parent() -> tuple[bool, str]:
    path = database_config.ensure_database_parent(database_config.DATABASE_URL)
    return Path(path).parent.exists(), "database parent ready"


def _database_init() -> tuple[bool, str]:
    result = initialize_database(database_config.DATABASE_URL)
    return result.get("status") == "ok", "database initialized"


def _auth_policy() -> tuple[bool, str]:
    policy = get_security_policy()
    return policy.auth_mode in {"local", "dev", "production"}, f"auth mode {policy.auth_mode}"


def _plan_config() -> tuple[bool, str]:
    module = importlib.import_module("src.config.plan_config")
    limits = module.get_plan_limits("free")
    return "max_reports_per_day" in limits, "plan config ready"


def _api_imports() -> tuple[bool, str]:
    importlib.import_module("src.api.v2.server")
    return True, "api imports ready"


def _no_committed_env() -> tuple[bool, str]:
    return not (PROJECT_ROOT / ".env").exists(), ".env not committed"


def _no_obvious_secret_patterns() -> tuple[bool, str]:
    scan_files = [PROJECT_ROOT / ".env.example", PROJECT_ROOT / "docker-compose.prod.example.yml"]
    for path in scan_files:
        if path.exists() and SECRET_PATTERN.search(path.read_text(encoding="utf-8")):
            return False, f"secret-like pattern in {_relative(path)}"
    return True, "no obvious secret patterns"


def _system_doctor_compatibility() -> tuple[bool, str]:
    result = run_system_health_check()
    return result.get("overall_status") in {"ok", "warning"}, f"system health {result.get('overall_status')}"


def run_startup_check() -> dict:
    checks = [
        _check("python_version", _python_version),
        _check("required_directories", _required_directories),
        _check("database_parent", _database_parent),
        _check("database_init", _database_init),
        _check("auth_policy", _auth_policy),
        _check("plan_config", _plan_config),
        _check("api_imports", _api_imports),
        _check("no_committed_env", _no_committed_env),
        _check("no_obvious_secret_patterns", _no_obvious_secret_patterns),
        _check("system_doctor_compatibility", _system_doctor_compatibility),
    ]
    errors = [check for check in checks if check["status"] == "error"]
    warnings: list[dict] = []
    return {"success": not errors, "checks": checks, "warnings": warnings, "errors": errors}


def main() -> int:
    result = run_startup_check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

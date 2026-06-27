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

from config.v5_deployment_config import get_v5_deployment_status


RISK_PATTERN = re.compile(
    r"(sk-[A-Za-z0-9]|ghp_[A-Za-z0-9]|xoxb-|-----BEGIN|"
    + "api"
    + r"_key\s*=|pass"
    + r"word\s*=|tok"
    + r"en\s*=|author"
    + r"ization\s*:|stripe\s+live)",
    re.IGNORECASE,
)


def run_v55_deployment_dry_run_check() -> dict:
    checks = [
        _check("v5_0_trading_modules", lambda: _modules_exist(["trading.order", "trading.paper_broker", "trading.paper_trading_runner"])),
        _check("v5_1_runtime_modules", lambda: _modules_exist(["runtime.trading_engine", "runtime.market_simulator", "runtime.event_bus"])),
        _check("v5_2_stability_modules", lambda: _modules_exist(["runtime.watchdog", "runtime.recovery_engine", "runtime.state_checkpoint"])),
        _check("v5_3_soak_modules", lambda: _modules_exist(["runtime.soak_test_runner", "runtime.synthetic_market", "runtime.consistency_validator"])),
        _check("v5_4_monitoring_module", lambda: _modules_exist(["runtime.monitoring_summary", "runtime.monitoring_report"])),
        _check("fastapi_app_import", _api_app_import),
        _check("monitoring_summary_endpoint", lambda: _api_endpoint("/api/v5/monitoring/summary")),
        _check("monitoring_health_endpoint", lambda: _api_endpoint("/api/v5/monitoring/health")),
        _check("monitoring_risk_endpoint", lambda: _api_endpoint("/api/v5/monitoring/risk")),
        _check("monitoring_soak_endpoint", lambda: _api_endpoint("/api/v5/monitoring/soak-report")),
        _check("runtime_missing_file_fallback", _runtime_fallback),
        _check("dockerfile", lambda: _exists("Dockerfile")),
        _check("docker_compose", lambda: _exists("docker-compose.yml")),
        _check("docker_compose_prod_example", lambda: _exists("docker-compose.prod.example.yml")),
        _check("env_example", lambda: _exists(".env.example")),
        _check("no_committed_env", lambda: (not (PROJECT_ROOT / ".env").exists(), "env file absent")),
        _check("readme_v55", lambda: _contains("README.md", "V5.5")),
        _check("review_package_v55", lambda: _contains("REVIEW_PACKAGE.md", "V5.5")),
        _check("no_credential_markers", _no_credential_markers),
        _check("real_trading_disabled", lambda: (get_v5_deployment_status()["real_trading"] is False, "real trading disabled")),
        _check("payment_live_absent", _payment_live_absent),
        _check("external_log_upload_absent", _external_log_upload_absent),
        _check("production_database_absent", _production_database_absent),
    ]
    errors = [check for check in checks if check["status"] == "error"]
    warnings = list(get_v5_deployment_status().get("warnings", []))
    return _sanitize_result(
        {
            "success": not errors,
            "deployment_ready": False,
            "dry_run_ready": not errors,
            "checks": checks,
            "warnings": warnings,
            "errors": errors,
            "safety": {
                "paper_trading": True,
                "real_trading": False,
                "broker_connected": False,
                "real_money_enabled": False,
                "production_deployment": False,
            },
        }
    )


def build_v55_deployment_payload() -> dict:
    check = run_v55_deployment_dry_run_check()
    status = get_v5_deployment_status()
    return _sanitize_result(
        {
            "version": "V5.5",
            "mode": "dry_run",
            "deployment_mode": status["deployment_mode"],
            "runtime_mode": status["runtime_mode"],
            "monitoring_mode": status["monitoring_mode"],
            "storage_mode": status["storage_mode"],
            "dry_run_ready": check["dry_run_ready"],
            "deployment_ready": False,
            "paper_trading": True,
            "real_trading": False,
            "broker_connected": False,
            "real_money_enabled": False,
            "production_deployment": False,
            "checks": check["checks"],
            "warnings": check["warnings"],
        }
    )


def _check(name: str, fn: Callable[[], tuple[bool, str]]) -> dict:
    try:
        ok, message = fn()
    except Exception as exc:
        return {"name": name, "status": "error", "message": type(exc).__name__}
    return {"name": name, "status": "ok" if ok else "error", "message": message}


def _modules_exist(module_names: list[str]) -> tuple[bool, str]:
    for module_name in module_names:
        importlib.import_module(module_name)
    return True, "modules ready"


def _api_app_import() -> tuple[bool, str]:
    module = importlib.import_module("src.api.v2.server")
    return bool(module.create_v2_api_app()), "api app ready"


def _api_endpoint(path: str) -> tuple[bool, str]:
    from src.api.v2.server import create_v2_api_app

    response = TestClient(create_v2_api_app()).get(path)
    return response.status_code == 200, f"status {response.status_code}"


def _runtime_fallback() -> tuple[bool, str]:
    from runtime.monitoring_data_reader import MonitoringDataReader
    from runtime.monitoring_summary import build_monitoring_summary

    reader = MonitoringDataReader(log_path="missing.log", checkpoint_path="missing.json", soak_report_path="missing.md")
    summary = build_monitoring_summary(reader)
    return summary["paper_trading"] is True and summary["real_trading"] is False, "fallback ready"


def _exists(relative_path: str) -> tuple[bool, str]:
    return (PROJECT_ROOT / relative_path).exists(), "present" if (PROJECT_ROOT / relative_path).exists() else "missing"


def _contains(relative_path: str, text: str) -> tuple[bool, str]:
    path = PROJECT_ROOT / relative_path
    if not path.exists():
        return False, "missing"
    return text in path.read_text(encoding="utf-8", errors="ignore"), "documented"


def _scan_files(paths: list[Path], pattern: re.Pattern[str]) -> tuple[bool, str]:
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else [item for item in root.rglob("*") if item.is_file()]
        for file_path in files:
            if file_path.suffix in {".pyc", ".png"}:
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            if pattern.search(text):
                return False, f"blocked marker in {_relative(file_path)}"
    return True, "clean"


def _no_credential_markers() -> tuple[bool, str]:
    return _scan_files(
        [
            PROJECT_ROOT / "config" / "v5_deployment_config.py",
            PROJECT_ROOT / "runtime" / "v55_deployment_report.py",
            PROJECT_ROOT / "scripts" / "run_v55_deployment_dry_run.py",
            PROJECT_ROOT / "web" / "frontend" / "app" / "v5-deployment",
        ],
        RISK_PATTERN,
    )


def _payment_live_absent() -> tuple[bool, str]:
    return _scan_files([PROJECT_ROOT / "config", PROJECT_ROOT / "runtime", PROJECT_ROOT / "scripts"], re.compile(r"stripe\s+live|live\s+payment", re.IGNORECASE))


def _external_log_upload_absent() -> tuple[bool, str]:
    return _scan_files([PROJECT_ROOT / "scripts" / "run_v55_deployment_dry_run.py", PROJECT_ROOT / "config" / "v5_deployment_config.py"], re.compile(r"upload\s+logs|external\s+log\s+upload", re.IGNORECASE))


def _production_database_absent() -> tuple[bool, str]:
    return _scan_files([PROJECT_ROOT / "config" / "v5_deployment_config.py", PROJECT_ROOT / "scripts" / "run_v55_deployment_dry_run.py"], re.compile(r"postgres://|mysql://|prod-db", re.IGNORECASE))


def _sanitize_result(value):
    text = json.dumps(value, default=str)
    text = text.replace(str(PROJECT_ROOT), "[repo]")
    return json.loads(text)


def _relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.name


def main() -> int:
    result = run_v55_deployment_dry_run_check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

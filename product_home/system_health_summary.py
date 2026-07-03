from __future__ import annotations

from pathlib import Path

from config.v5_product_home_config import get_product_home_status
from local_launcher.environment_checker import run_environment_check
from local_launcher.port_checker import check_launcher_ports
from product_home.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_system_health_summary() -> dict:
    env = run_environment_check()
    ports = check_launcher_ports()
    warnings = list(get_product_home_status().get("warnings", []))
    warnings.extend(env.get("warnings", []))
    warnings.extend(ports.get("warnings", []))
    errors = list(env.get("errors", []))
    latest_reports = sorted((PROJECT_ROOT / "reports").glob("v5_*_report.md"))
    items = [
        {"name": "backend_status_placeholder", "status": "available", "detail": "FastAPI local entry exists"},
        {"name": "frontend_status_placeholder", "status": "available", "detail": "Next.js app entry exists"},
        {"name": "local_launcher_status", "status": "available", "detail": "V5.39 launcher package present"},
        {"name": "system_doctor_placeholder", "status": "not_run", "detail": "Use scripts/system_doctor.py for live check"},
        {"name": "pytest_placeholder", "status": "not_run", "detail": "Use python -m pytest for full suite"},
        {"name": "security_scan_placeholder", "status": "not_run", "detail": "Product home performs payload safety checks only"},
        {"name": "latest_report_summary", "status": "available" if latest_reports else "empty", "detail": latest_reports[-1].name if latest_reports else "No local reports found"},
    ]
    health = "FAIL" if errors else "WARNING" if warnings else "OK"
    return {"system_health": health, "items": items, "warnings": warnings, "errors": errors, **boundary()}


def summarize_system_health(summary: dict) -> dict:
    return {
        "system_health": summary.get("system_health", "FAIL"),
        "item_count": len(summary.get("items", [])),
        "warning_count": len(summary.get("warnings", [])),
        "error_count": len(summary.get("errors", [])),
        **boundary(),
    }

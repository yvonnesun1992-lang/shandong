from __future__ import annotations

import os


VALID_DEPLOYMENT_MODES = {"local", "dry_run", "production_planned"}
VALID_RUNTIME_MODES = {"paper", "live_paper_planned", "production_planned"}
VALID_MONITORING_MODES = {"local", "api", "external_planned"}
VALID_STORAGE_MODES = {"local_files", "database_planned"}


def get_v5_deployment_mode() -> str:
    return _safe_choice("SHANDONG_V5_DEPLOYMENT_MODE", "dry_run", VALID_DEPLOYMENT_MODES)


def get_v5_runtime_mode() -> str:
    mode = _safe_choice("SHANDONG_V5_RUNTIME_MODE", "paper", VALID_RUNTIME_MODES)
    return "paper" if mode == "production_planned" else mode


def get_v5_monitoring_mode() -> str:
    mode = _safe_choice("SHANDONG_V5_MONITORING_MODE", "local", VALID_MONITORING_MODES)
    return "local" if mode == "external_planned" else mode


def get_v5_storage_mode() -> str:
    mode = _safe_choice("SHANDONG_V5_STORAGE_MODE", "local_files", VALID_STORAGE_MODES)
    return "local_files" if mode == "database_planned" else mode


def get_v5_deployment_status() -> dict:
    return {
        "version": "V5.5",
        "deployment_mode": get_v5_deployment_mode(),
        "runtime_mode": get_v5_runtime_mode(),
        "monitoring_mode": get_v5_monitoring_mode(),
        "storage_mode": get_v5_storage_mode(),
        "paper_trading": True,
        "real_trading": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "production_deployment": False,
        "dry_run_ready": True,
        "deployment_ready": False,
        "warnings": _safety_warnings(),
    }


def _safe_choice(name: str, default: str, allowed: set[str]) -> str:
    value = os.getenv(name, default).strip().lower()
    return value if value in allowed else default


def _flag_requested(name: str) -> bool:
    return os.getenv(name, "false").strip().lower() in {"1", "true", "yes", "on"}


def _safety_warnings() -> list[str]:
    warnings = []
    if _flag_requested("SHANDONG_V5_ENABLE_REAL_TRADING"):
        warnings.append("real trading request ignored for dry run")
    if _flag_requested("SHANDONG_V5_ENABLE_BROKER"):
        warnings.append("broker request ignored for dry run")
    if _flag_requested("SHANDONG_V5_ENABLE_REAL_MONEY"):
        warnings.append("real money request ignored for dry run")
    return warnings

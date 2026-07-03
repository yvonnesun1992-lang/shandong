from __future__ import annotations

import os


VERSION = "V5.42"
LOCAL_RUN_DOCTOR_MODE = "local_run_doctor_only"


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_local_run_doctor_mode() -> str:
    return LOCAL_RUN_DOCTOR_MODE


def get_local_run_doctor_status() -> dict:
    warnings: list[str] = []
    requested_mode = os.getenv("SHANDONG_V5_LOCAL_RUN_DOCTOR_MODE", "").strip()
    if requested_mode and requested_mode != LOCAL_RUN_DOCTOR_MODE:
        warnings.append("local run doctor mode override requested but blocked in V5.42")
    requested_flags = {
        "SHANDONG_V5_ENABLE_LOCAL_RUN_DOCTOR_RUNTIME": "local run doctor runtime requested but blocked in V5.42",
        "SHANDONG_V5_ENABLE_AUTO_FIX": "auto fix requested but blocked in V5.42",
        "SHANDONG_V5_ENABLE_INSTALL_DEPENDENCIES": "install dependencies requested but blocked in V5.42",
        "SHANDONG_V5_ENABLE_EXTERNAL_NETWORK": "external network requested but blocked in V5.42",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.42",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.42",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.42",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.42",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.42",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)
    return {
        "version": VERSION,
        "local_run_doctor_mode": get_local_run_doctor_mode(),
        "local_run_doctor_only": True,
        "localhost_only": True,
        "doctor_runtime_enabled": False,
        "auto_fix_enabled": False,
        "install_dependencies_enabled": False,
        "external_network_enabled": False,
        "broker_connected": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "balance_read_enabled": False,
        "position_read_enabled": False,
        "order_preview_enabled": False,
        "order_submission_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": warnings,
    }

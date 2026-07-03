from __future__ import annotations

import os


VERSION = "V5.41"
LOCAL_E2E_MODE = "local_e2e_verification_only"


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_local_e2e_mode() -> str:
    return LOCAL_E2E_MODE


def get_local_e2e_status() -> dict:
    warnings: list[str] = []
    requested_mode = os.getenv("SHANDONG_V5_LOCAL_E2E_MODE", "").strip()
    if requested_mode and requested_mode != LOCAL_E2E_MODE:
        warnings.append("local e2e mode override requested but blocked in V5.41")
    requested_flags = {
        "SHANDONG_V5_ENABLE_LOCAL_E2E_RUNTIME": "local e2e runtime requested but blocked in V5.41",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.41",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.41",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.41",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.41",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.41",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)
    return {
        "version": VERSION,
        "local_e2e_mode": get_local_e2e_mode(),
        "local_e2e_verification_only": True,
        "local_e2e_runtime_enabled": False,
        "localhost_only": True,
        "backend_start_allowed": True,
        "frontend_start_allowed": True,
        "browser_check_allowed": True,
        "api_smoke_test_allowed": True,
        "log_write_test_allowed": True,
        "report_generation_allowed": True,
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

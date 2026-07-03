from __future__ import annotations

import os


VERSION = "V5.40"
PRODUCT_HOME_MODE = "product_home_only"


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_product_home_mode() -> str:
    return PRODUCT_HOME_MODE


def get_product_home_status() -> dict:
    warnings: list[str] = []
    requested_mode = os.getenv("SHANDONG_V5_PRODUCT_HOME_MODE", "").strip()
    if requested_mode and requested_mode != PRODUCT_HOME_MODE:
        warnings.append("product home mode override requested but blocked in V5.40")
    requested_flags = {
        "SHANDONG_V5_ENABLE_PRODUCT_HOME_RUNTIME": "product home runtime requested but blocked in V5.40",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.40",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.40",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.40",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.40",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.40",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)
    return {
        "version": VERSION,
        "product_home_mode": get_product_home_mode(),
        "product_home_only": True,
        "product_home_runtime_enabled": False,
        "localhost_only": True,
        "dashboard_read_only": True,
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

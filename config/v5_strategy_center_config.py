from __future__ import annotations

import os


VERSION = "V5.46"
STRATEGY_CENTER_MODE = "strategy_center_only"


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_strategy_center_mode() -> str:
    return STRATEGY_CENTER_MODE


def get_strategy_center_status() -> dict:
    warnings: list[str] = []
    requested_mode = os.getenv("SHANDONG_V5_STRATEGY_CENTER_MODE", "").strip()
    if requested_mode and requested_mode != STRATEGY_CENTER_MODE:
        warnings.append("strategy center mode override requested but blocked in V5.46")

    requested_flags = {
        "SHANDONG_V5_ENABLE_STRATEGY_CENTER_RUNTIME": "strategy center runtime requested but blocked in V5.46",
        "SHANDONG_V5_ENABLE_ADVANCED_CODE_VIEW": "advanced code view requested but blocked in V5.46",
        "SHANDONG_V5_ENABLE_REAL_TRADING": "real trading requested but blocked in V5.46",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.46",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.46",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.46",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.46",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.46",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)

    return {
        "version": VERSION,
        "strategy_center_mode": get_strategy_center_mode(),
        "strategy_center_only": True,
        "localhost_only": True,
        "strategy_center_runtime_enabled": False,
        "user_friendly_strategy_library": True,
        "code_editor_visible_by_default": False,
        "advanced_code_view_enabled": False,
        "one_click_backtest_enabled": True,
        "paper_trading_preview_enabled": True,
        "real_trading_enabled": False,
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

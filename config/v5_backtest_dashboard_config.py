from __future__ import annotations

import os


VERSION = "V5.47"
BACKTEST_DASHBOARD_MODE = "backtest_dashboard_only"


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_backtest_dashboard_mode() -> str:
    return BACKTEST_DASHBOARD_MODE


def get_backtest_dashboard_status() -> dict:
    warnings: list[str] = []
    requested_mode = os.getenv("SHANDONG_V5_BACKTEST_DASHBOARD_MODE", "").strip()
    if requested_mode and requested_mode != BACKTEST_DASHBOARD_MODE:
        warnings.append("backtest dashboard mode override requested but blocked in V5.47")

    requested_flags = {
        "SHANDONG_V5_ENABLE_BACKTEST_DASHBOARD_RUNTIME": "backtest dashboard runtime requested but blocked in V5.47",
        "SHANDONG_V5_ENABLE_ADVANCED_METRICS_EXPANDED": "advanced metrics expanded requested but blocked in V5.47",
        "SHANDONG_V5_ENABLE_REAL_TRADING": "real trading requested but blocked in V5.47",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.47",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.47",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.47",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.47",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.47",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)

    return {
        "version": VERSION,
        "backtest_dashboard_mode": get_backtest_dashboard_mode(),
        "backtest_dashboard_only": True,
        "localhost_only": True,
        "backtest_dashboard_runtime_enabled": False,
        "user_friendly_backtest_report": True,
        "advanced_metrics_collapsed_by_default": True,
        "one_click_rebacktest_enabled": True,
        "paper_trading_entry_enabled": True,
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

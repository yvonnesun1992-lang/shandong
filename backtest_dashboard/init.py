from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.47",
        "backtest_dashboard_only": True,
        "localhost_only": True,
        "user_friendly_backtest_report": True,
        "advanced_metrics_collapsed_by_default": True,
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
    }

from __future__ import annotations

from product_home.init import boundary


def build_paper_trading_summary() -> dict:
    return {
        "paper_trading_available": True,
        "broker_connected": False,
        "sandbox_api_enabled": False,
        "order_submission_enabled": False,
        "latest_paper_account_placeholder": {"mode": "paper", "status": "not_live_account"},
        "latest_paper_performance_placeholder": {"status": "available_via_local_reports"},
        "latest_signal_placeholder": {"status": "local_alpha_signal_only"},
        **boundary(),
    }

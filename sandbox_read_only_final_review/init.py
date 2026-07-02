from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.38",
        "read_only_final_review_only": True,
        "final_review_runtime_enabled": False,
        "final_review_passed": False,
        "read_only_connector_allowed": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "position_read_enabled": False,
        "balance_read_enabled": False,
        "order_preview_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.30",
        "review_board_only": True,
        "review_runtime_enabled": False,
        "reviewer_approval_enabled": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }

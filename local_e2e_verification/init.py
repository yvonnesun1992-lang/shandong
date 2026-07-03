from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.41",
        "local_e2e_verification_only": True,
        "localhost_only": True,
        "local_e2e_runtime_enabled": False,
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

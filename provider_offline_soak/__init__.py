from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.25",
        "offline_soak_only": True,
        "soak_runtime_enabled": False,
        "sandbox_api_enabled": False,
        "account_read_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }

from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.27",
        "vault_design_only": True,
        "vault_runtime_enabled": False,
        "secret_read_enabled": False,
        "secret_write_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "order_submission_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }

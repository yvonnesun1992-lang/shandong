from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.32",
        "controlled_blueprint_only": True,
        "controlled_enablement_runtime_enabled": False,
        "controlled_go_enabled": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "order_preview_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }

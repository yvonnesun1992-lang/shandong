from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.35",
        "read_only_fault_injection_only": True,
        "fault_injection_runtime_enabled": False,
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

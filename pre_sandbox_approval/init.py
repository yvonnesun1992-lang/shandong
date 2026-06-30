from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.28",
        "approval_gate_only": True,
        "approval_runtime_enabled": False,
        "operator_approval_granted": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "broker_connected": False,
        "order_submission_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }

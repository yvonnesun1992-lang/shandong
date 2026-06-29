from __future__ import annotations


CONNECTOR_DESIGN_BOUNDARY = {
    "version": "V5.21",
    "design_only": True,
    "connector_runtime_enabled": False,
    "sandbox_api_enabled": False,
    "account_read_enabled": False,
    "order_submission_enabled": False,
    "broker_connected": False,
    "real_money_enabled": False,
    "paper_trading": True,
}


def boundary() -> dict:
    return CONNECTOR_DESIGN_BOUNDARY.copy()

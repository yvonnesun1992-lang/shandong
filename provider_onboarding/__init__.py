from __future__ import annotations


ONBOARDING_BOUNDARY = {
    "runbook_only": True,
    "provider_portal_access_enabled": False,
    "sandbox_api_enabled": False,
    "api_key_creation_enabled": False,
    "broker_connected": False,
    "real_orders_enabled": False,
    "real_money_enabled": False,
    "paper_trading": True,
}


def boundary() -> dict:
    return ONBOARDING_BOUNDARY.copy()

from __future__ import annotations

from provider_selection import PROVIDER_BOUNDARY


API_PERMISSIONS = [
    "API key creation process",
    "API secret storage plan",
    "read account permission",
    "read position permission",
    "market data permission",
    "submit order permission",
    "cancel order permission",
    "order status permission",
    "sandbox / paper endpoint permission",
    "IP whitelist requirement",
    "rate limit documentation",
    "credential rotation procedure",
]


def build_api_permission_checklist(provider: str = "alpaca") -> dict:
    permissions = [{"permission": item, "confirmed": False} for item in API_PERMISSIONS]
    return {"version": "V5.19", "provider": provider, "api_ready": False, "permissions": permissions, "blocking_items": API_PERMISSIONS, "credential_storage_required": "future_vault", **PROVIDER_BOUNDARY}

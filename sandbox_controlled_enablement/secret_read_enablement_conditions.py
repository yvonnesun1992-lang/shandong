from __future__ import annotations

from sandbox_controlled_enablement.init import boundary


SECRET_READ_CONDITIONS = [
    "vault runtime live",
    "secret reference validated",
    "secret scope limited to sandbox",
    "read-only secret preferred",
    "operator approval required",
    "audit event required",
    "secret value never logged",
    "frontend cannot access",
    "emergency revoke ready",
]


def build_secret_read_enablement_conditions(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "conditions": [{"name": item, "met": False} for item in SECRET_READ_CONDITIONS],
        "secret_read_ready": False,
        "secret_read_enabled": False,
        "blocking_items": SECRET_READ_CONDITIONS.copy(),
    }

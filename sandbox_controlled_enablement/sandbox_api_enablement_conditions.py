from __future__ import annotations

from sandbox_controlled_enablement.init import boundary


SANDBOX_API_CONDITIONS = [
    "sandbox credentials available through vault",
    "sandbox endpoint approved",
    "provider docs verified",
    "network egress policy approved",
    "rate limit policy configured",
    "retry policy configured",
    "read-only mode first",
    "kill switch active",
    "audit logging active",
]


def build_sandbox_api_enablement_conditions(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "conditions": [{"name": item, "met": False} for item in SANDBOX_API_CONDITIONS],
        "sandbox_api_ready": False,
        "sandbox_api_enabled": False,
        "blocking_items": SANDBOX_API_CONDITIONS.copy(),
    }

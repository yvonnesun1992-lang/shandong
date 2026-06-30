from __future__ import annotations

from sandbox_controlled_enablement.init import boundary


ACCOUNT_READ_CONDITIONS = [
    "sandbox API approved",
    "read-only credential scope",
    "account identifier redaction policy",
    "balance redaction policy",
    "position redaction policy",
    "audit logging",
    "rate limit guard",
    "no order permission required",
]


def build_account_read_enablement_conditions(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "conditions": [{"name": item, "met": False} for item in ACCOUNT_READ_CONDITIONS],
        "account_read_ready": False,
        "account_read_enabled": False,
        "blocking_items": ACCOUNT_READ_CONDITIONS.copy(),
    }

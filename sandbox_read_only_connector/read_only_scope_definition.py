from __future__ import annotations

from sandbox_read_only_connector.init import boundary


ALLOWED_FUTURE_ACTIONS = [
    "validate connector config",
    "validate vault reference placeholder",
    "validate read-only credential scope",
    "read sandbox account status in future",
    "read sandbox cash balance in future",
    "read sandbox buying power in future",
    "read sandbox positions in future",
    "read sandbox order history in future as read-only",
    "write audit event",
]

DISALLOWED_ACTIONS = [
    "order preview execution",
    "order submission",
    "cancel order",
    "modify order",
    "transfer funds",
    "real account access",
    "real money access",
    "frontend credential access",
    "raw provider payload storage",
]


def build_read_only_scope_definition(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "read_only_scope": {
            "allowed_future_actions": ALLOWED_FUTURE_ACTIONS.copy(),
            "disallowed_actions": DISALLOWED_ACTIONS.copy(),
            "network_calls_enabled": False,
            "runtime_enabled": False,
        },
        "scope_ready": False,
        "blocking_items": ["future approval required", "runtime disabled", "sandbox API disabled"],
    }

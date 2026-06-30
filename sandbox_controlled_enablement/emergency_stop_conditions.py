from __future__ import annotations

from sandbox_controlled_enablement.init import boundary


STOP_CONDITIONS = [
    "any secret leakage",
    "unexpected sandbox API response",
    "account read mismatch",
    "rate limit storm",
    "audit write failure",
    "kill switch unavailable",
    "rollback unavailable",
    "unexpected order submission attempt",
    "unknown provider payload",
    "operator cancellation",
]


def build_emergency_stop_conditions(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "emergency_stop_conditions": [{"name": item, "action": "stop future enablement"} for item in STOP_CONDITIONS],
        "emergency_stop_ready": False,
        "current_action": "NO_RUNTIME_TO_STOP",
    }

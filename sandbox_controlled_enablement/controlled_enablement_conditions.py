from __future__ import annotations

from sandbox_controlled_enablement.init import boundary


CONDITION_NAMES = [
    "V5.31 final preflight packet reviewed",
    "review board decision changed through future authorized process",
    "credential vault live and tested",
    "sandbox account approved",
    "provider docs independently verified",
    "sandbox API endpoint approved",
    "market data permissions confirmed",
    "read-only sandbox scope approved",
    "immutable audit storage live",
    "kill switch live-tested",
    "rollback rehearsal completed",
    "compliance signoff completed",
    "operator training completed",
    "emergency contact path verified",
]


def build_controlled_enablement_conditions(provider: str = "alpaca") -> dict:
    conditions = [{"name": name, "met": False, "requires_future_approval": True} for name in CONDITION_NAMES]
    return {
        **boundary(),
        "provider": provider,
        "controlled_go_conditions": conditions,
        "conditions_met": False,
        "controlled_go_enabled": False,
        "blocking_items": CONDITION_NAMES.copy(),
    }

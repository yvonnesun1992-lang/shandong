from __future__ import annotations

from provider_onboarding import boundary


STEPS = [
    "manual approval mandatory",
    "dual confirmation future requirement",
    "order preview required",
    "notional limit required",
    "symbol allowlist required",
    "position limit required",
    "daily loss limit required",
    "kill switch required",
    "audit event required",
    "rollback trigger required",
]


def build_approval_risk_runbook(provider: str) -> dict:
    return {
        "provider": provider,
        "approval_risk_ready": False,
        "steps": STEPS.copy(),
        "blocking_items": [
            "manual approval gate must be enforced before sandbox connection",
            "kill switch must be tested before sandbox connection",
            "order preview must remain mandatory",
        ],
        "manual_approval_required": True,
        "kill_switch_required": True,
        **boundary(),
    }

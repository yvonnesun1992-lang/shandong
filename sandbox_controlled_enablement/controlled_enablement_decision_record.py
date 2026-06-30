from __future__ import annotations

from sandbox_controlled_enablement.init import boundary


def build_controlled_enablement_decision(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "decision": "CONTROLLED_GO_BLOCKED",
        "controlled_go_requested": False,
        "simulated_approval": False,
        "reason": [
            "V5.32 is controlled enablement blueprint only",
            "sandbox API, secret read, account read, order preview, and order submission remain disabled",
            "future approval cannot be simulated in this version",
        ],
    }


def evaluate_controlled_enablement_decision(context: dict | None = None) -> dict:
    context = context or {}
    decision = build_controlled_enablement_decision(context.get("provider", "alpaca"))
    decision["controlled_go_requested"] = bool(context.get("controlled_go_requested"))
    decision["simulated_approval"] = bool(context.get("simulated_approval"))
    if decision["controlled_go_requested"] or decision["simulated_approval"]:
        decision["warnings"] = ["controlled GO request observed but blocked in V5.32"]
    else:
        decision["warnings"] = []
    return decision

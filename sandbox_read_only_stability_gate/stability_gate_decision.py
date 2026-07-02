from __future__ import annotations

from sandbox_read_only_stability_gate.init import boundary


def evaluate_stability_gate_decision(context: dict | None = None) -> dict:
    context = context or {}
    return {
        **boundary(),
        "provider": context.get("provider", "alpaca"),
        "decision": "STABILITY_GATE_BLOCKED",
        "stability_gate_passed": False,
        "read_only_connector_allowed": False,
        "replay_passed_observed": bool(context.get("replay_passed")),
        "fault_injection_passed_observed": bool(context.get("fault_injection_passed")),
        "simulated_approval_ignored": bool(context.get("simulated_approval")),
        "warnings": ["V5.36 stability gate is evidence-only and cannot unlock connector access"],
    }


def build_stability_gate_decision(provider: str = "alpaca") -> dict:
    return evaluate_stability_gate_decision({"provider": provider, "replay_passed": True, "fault_injection_passed": True})

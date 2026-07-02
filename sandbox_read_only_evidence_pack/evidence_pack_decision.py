from __future__ import annotations

from sandbox_read_only_evidence_pack.init import boundary


def evaluate_evidence_pack_decision(context: dict | None = None) -> dict:
    context = context or {}
    return {
        **boundary(),
        "provider": context.get("provider", "alpaca"),
        "decision": "READ_ONLY_EVIDENCE_ONLY",
        "evidence_pack_passed": False,
        "read_only_connector_allowed": False,
        "evidence_complete_observed": bool(context.get("evidence_complete")),
        "stability_gate_passed_observed": bool(context.get("stability_gate_passed")),
        "simulated_approval_ignored": bool(context.get("simulated_approval")),
        "warnings": ["V5.37 evidence pack is documentation-only and cannot unlock connector access"],
    }


def build_evidence_pack_decision(provider: str = "alpaca") -> dict:
    return evaluate_evidence_pack_decision({"provider": provider, "evidence_complete": True, "stability_gate_passed": True})


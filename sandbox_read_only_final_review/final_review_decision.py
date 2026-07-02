from __future__ import annotations

from sandbox_read_only_final_review.init import boundary


def evaluate_final_review_decision(context: dict | None = None) -> dict:
    context = context or {}
    return {
        **boundary(),
        "provider": context.get("provider", "alpaca"),
        "decision": "READ_ONLY_FINAL_REVIEW_ONLY",
        "final_review_passed": False,
        "read_only_connector_allowed": False,
        "evidence_review_ready_observed": bool(context.get("evidence_review_ready")),
        "risk_acceptance_ready_observed": bool(context.get("risk_acceptance_ready")),
        "simulated_approval_ignored": bool(context.get("simulated_approval")),
        "warnings": ["V5.38 final review board is review-only and cannot unlock connector access"],
    }


def build_final_review_decision(provider: str = "alpaca") -> dict:
    return evaluate_final_review_decision({"provider": provider, "evidence_review_ready": True, "risk_acceptance_ready": False})


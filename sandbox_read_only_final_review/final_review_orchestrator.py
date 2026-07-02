from __future__ import annotations

from sandbox_read_only_final_review.evidence_review_matrix import build_evidence_review_matrix
from sandbox_read_only_final_review.final_review_audit_trail import build_final_review_audit_trail
from sandbox_read_only_final_review.final_review_charter import build_final_review_charter
from sandbox_read_only_final_review.final_review_decision import build_final_review_decision
from sandbox_read_only_final_review.final_review_safety_validator import build_final_review_safety_summary
from sandbox_read_only_final_review.init import boundary
from sandbox_read_only_final_review.missing_requirement_register import build_missing_requirement_register
from sandbox_read_only_final_review.reviewer_role_matrix import build_reviewer_role_matrix
from sandbox_read_only_final_review.risk_acceptance_matrix import build_risk_acceptance_matrix


def build_read_only_final_review(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "charter": build_final_review_charter(provider),
        "roles": build_reviewer_role_matrix(provider),
        "evidence": build_evidence_review_matrix(provider),
        "risks": build_risk_acceptance_matrix(provider),
        "missing": build_missing_requirement_register(provider),
        "decision_record": build_final_review_decision(provider),
        "audit": build_final_review_audit_trail(provider),
        "safety": build_final_review_safety_summary(),
    }


def summarize_read_only_final_review(result: dict) -> dict:
    warnings: list[str] = []
    errors: list[str] = []
    for key in ["charter", "roles", "evidence", "risks", "missing", "decision_record", "audit", "safety"]:
        warnings.extend(result.get(key, {}).get("warnings", []))
        errors.extend(result.get(key, {}).get("errors", []))
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "evidence_review_ready": result.get("evidence", {}).get("evidence_review_ready", False),
        "risk_acceptance_ready": result.get("risks", {}).get("risk_acceptance_ready", False),
        "missing_count": result.get("missing", {}).get("missing_count", 0),
        "final_review_passed": False,
        "read_only_connector_allowed": False,
        "decision": "READ_ONLY_FINAL_REVIEW_ONLY",
        "errors": errors,
        "warnings": warnings,
        "verdict": "FAIL" if errors else ("WARNING" if warnings else "PASS"),
    }


from __future__ import annotations

from sandbox_review_board.evidence_review_matrix import build_evidence_review_matrix
from sandbox_review_board.go_no_go_decision_record import build_go_no_go_decision
from sandbox_review_board.init import boundary
from sandbox_review_board.readiness_scoring import build_readiness_score_summary
from sandbox_review_board.review_audit_trail import build_review_audit_trail
from sandbox_review_board.review_board_charter import build_review_board_charter
from sandbox_review_board.review_board_safety_validator import build_review_board_safety_summary
from sandbox_review_board.reviewer_role_matrix import build_reviewer_role_matrix
from sandbox_review_board.risk_acceptance_matrix import build_risk_acceptance_matrix


def build_review_board_packet(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "charter": build_review_board_charter(provider),
        "roles": build_reviewer_role_matrix(provider),
        "evidence": build_evidence_review_matrix(provider),
        "risks": build_risk_acceptance_matrix(provider),
        "score": build_readiness_score_summary(provider),
        "decision": build_go_no_go_decision(provider),
        "audit": build_review_audit_trail(provider),
        "safety": build_review_board_safety_summary(),
    }


def summarize_review_board_packet(result: dict) -> dict:
    warnings = []
    warnings.extend(result.get("evidence", {}).get("warnings", []))
    warnings.extend(result.get("safety", {}).get("warnings", []))
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "verdict": "WARNING" if warnings else "PASS",
        "decision": result.get("decision", {}).get("decision", "NO_GO"),
        "readiness_score": result.get("score", {}).get("readiness_score", 0.0),
        "ready_for_sandbox_dry_run": False,
        "safe": result.get("safety", {}).get("safe", False),
        "warnings": warnings,
    }

from __future__ import annotations

from sandbox_review_board.init import boundary


def compute_readiness_score(provider: str = "alpaca") -> dict:
    breakdown = {
        "evidence_completeness": 0.7,
        "replay_coverage": 0.8,
        "fault_coverage": 0.8,
        "soak_stability": 0.7,
        "vault_design_completeness": 0.7,
        "approval_gate_completeness": 0.8,
        "launch_plan_completeness": 0.8,
        "safety_boundary_strength": 1.0,
        "remaining_blockers": 0.0,
    }
    score = round(sum(breakdown.values()) / len(breakdown), 3)
    return {
        **boundary(),
        "provider": provider,
        "readiness_score": score,
        "score_breakdown": breakdown,
        "ready_for_sandbox_dry_run": False,
        "score_unlocks_sandbox": False,
    }


def build_readiness_score_summary(provider: str = "alpaca") -> dict:
    return compute_readiness_score(provider)

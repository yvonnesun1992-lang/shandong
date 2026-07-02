from __future__ import annotations

from sandbox_read_only_final_review.init import boundary


def build_final_review_charter(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "charter": {
            "purpose": "final review of local read-only connector evidence",
            "scope": "review V5.34-V5.37 evidence for future sandbox readiness planning",
            "out_of_scope": [
                "sandbox API connection",
                "credential or secret read",
                "account, balance, or position read",
                "order preview or submission",
                "real money",
            ],
            "evidence_inputs": ["V5.34 mock replay", "V5.35 fault injection", "V5.36 stability gate", "V5.37 evidence pack"],
            "decision_authority": "review-only",
            "approval_limitations": "cannot approve real sandbox, secret, account, balance, position, or order paths",
            "no_execution_policy": "final review board cannot execute connector actions",
            "escalation_policy": "future real sandbox work requires a separate approved release",
            "allowed_decisions": ["READ_ONLY_FINAL_REVIEW_ONLY", "BLOCKED", "REVIEW_REQUIRED"],
        },
        "warnings": [],
    }


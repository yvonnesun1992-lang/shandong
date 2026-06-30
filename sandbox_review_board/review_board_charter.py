from __future__ import annotations

from sandbox_review_board.init import boundary


def build_review_board_charter(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "charter": {
            "purpose": "Review readiness for a future sandbox dry-run without executing it.",
            "scope": ["evidence review", "risk review", "readiness scoring", "NO_GO decision record"],
            "out_of_scope": ["sandbox API approval", "secret read approval", "account read approval", "order submission approval"],
            "decision_authority": ["NO_GO", "REVIEW_REQUIRED", "BLOCKED"],
            "required_evidence": ["V5.26 evidence pack", "V5.27 vault design", "V5.28 approval gate", "V5.29 launch plan"],
            "required_reviewers": ["strategy_owner", "technical_reviewer", "risk_reviewer", "compliance_reviewer", "security_reviewer", "operations_reviewer"],
            "approval_limitations": {
                "can_approve_sandbox_api": False,
                "can_approve_secret_read": False,
                "can_approve_account_read": False,
                "can_approve_order_submission": False,
            },
            "escalation_policy": "Escalate blockers to a future production readiness process.",
            "no_execution_policy": True,
        },
    }

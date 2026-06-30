from __future__ import annotations

from sandbox_review_board.init import boundary


def build_reviewer_role_matrix(provider: str = "alpaca") -> dict:
    responsibilities = {
        "strategy_owner": ["confirm strategy scope remains unchanged"],
        "technical_reviewer": ["review dry-run launch plan and integration boundaries"],
        "risk_reviewer": ["review risk blockers and kill switch requirements"],
        "compliance_reviewer": ["review disclosure and provider terms requirements"],
        "security_reviewer": ["review vault design and credential boundaries"],
        "operations_reviewer": ["review runbook, rollback, audit, and monitoring gaps"],
        "emergency_reviewer": ["review emergency stop and rollback path"],
    }
    return {
        **boundary(),
        "provider": provider,
        "roles": {
            role: {
                "responsibilities": items,
                "required_for_review": role != "emergency_reviewer",
                "can_approve_sandbox_api": False,
                "can_approve_secret_read": False,
                "can_approve_account_read": False,
                "can_approve_order_submission": False,
                "can_override_no_go": False,
            }
            for role, items in responsibilities.items()
        },
    }

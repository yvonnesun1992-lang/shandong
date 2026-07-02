from __future__ import annotations

from sandbox_read_only_final_review.init import boundary

ROLES = [
    "strategy_owner",
    "technical_reviewer",
    "risk_reviewer",
    "compliance_reviewer",
    "security_reviewer",
    "operations_reviewer",
    "emergency_reviewer",
]


def build_reviewer_role_matrix(provider: str = "alpaca") -> dict:
    roles = []
    for role in ROLES:
        roles.append(
            {
                "role": role,
                "responsibilities": [f"review {role.replace('_', ' ')} evidence"],
                "required_for_review": True,
                "can_approve_sandbox_api": False,
                "can_approve_secret_read": False,
                "can_approve_account_read": False,
                "can_approve_balance_read": False,
                "can_approve_position_read": False,
                "can_approve_order_preview": False,
                "can_approve_order_submission": False,
                "can_override_blocked_decision": False,
            }
        )
    return {**boundary(), "provider": provider, "roles": roles, "warnings": []}


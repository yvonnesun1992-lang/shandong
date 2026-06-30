from __future__ import annotations

from pre_sandbox_approval.init import boundary


def build_operator_role_policy() -> dict:
    roles = {
        "strategy_owner": {"approval_enabled": False, "scope": "strategy intent confirmation only"},
        "risk_operator": {"approval_enabled": False, "scope": "risk limit acknowledgement only"},
        "technical_operator": {"approval_enabled": False, "scope": "dry-run preparation only"},
        "compliance_reviewer": {"approval_enabled": False, "scope": "disclosure acknowledgement only"},
        "emergency_operator": {"approval_enabled": False, "scope": "kill switch only"},
    }
    return {
        **boundary(),
        "roles": roles,
        "rules": {
            "single_operator_can_approve_order_submission": False,
            "technical_operator_can_approve_dry_run_only": True,
            "risk_operator_must_approve_risk_limit": True,
            "compliance_reviewer_must_confirm_disclosure": True,
            "emergency_operator_kill_switch_only": True,
        },
    }

from __future__ import annotations

from pre_sandbox_approval.init import boundary


def build_approval_request_schema(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "approval_request_id_placeholder": "APPROVAL_REQUEST_PLACEHOLDER",
        "provider": provider,
        "requested_action": "sandbox_dry_run_preparation",
        "requested_environment": "sandbox_placeholder",
        "required_evidence_refs": [
            "V5.26 sandbox readiness evidence pack",
            "V5.27 credential vault interface design",
            "provider onboarding runbook",
            "connector design",
            "mock contract test",
            "offline replay",
            "fault injection",
            "offline soak",
        ],
        "required_operator_role": ["strategy_owner", "risk_operator", "technical_operator", "compliance_reviewer"],
        "risk_acknowledgement_required": True,
        "compliance_acknowledgement_required": True,
        "rollback_plan_required": True,
        "kill_switch_required": True,
        "expires_at_placeholder": "EXPIRY_TIMESTAMP_PLACEHOLDER",
        "external_system_connected": False,
        "real_user_identity_used": False,
    }

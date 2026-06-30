from __future__ import annotations

from pre_sandbox_approval.init import boundary


def build_approval_audit_event(context: dict | None = None) -> dict:
    context = context or {}
    return {
        **boundary(),
        "approval_audit_id_placeholder": "APPROVAL_AUDIT_PLACEHOLDER",
        "approval_request_id_placeholder": "APPROVAL_REQUEST_PLACEHOLDER",
        "provider": context.get("provider", "alpaca"),
        "requested_action": context.get("requested_action", "sandbox_dry_run_preparation"),
        "decision": "BLOCKED",
        "actor_placeholder": "OPERATOR_PLACEHOLDER",
        "timestamp_placeholder": "AUDIT_TIMESTAMP_PLACEHOLDER",
        "raw_secret_logged": False,
        "provider_payload_redacted": True,
    }


def build_approval_audit_trail(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "audit_enabled": False,
        "events": [build_approval_audit_event({"provider": provider})],
        "external_log_upload": False,
    }

from __future__ import annotations

from sandbox_dry_run_launch.init import boundary


def build_launch_audit_event(provider: str = "alpaca", action: str = "plan_review") -> dict:
    return {
        **boundary(),
        "launch_audit_id_placeholder": "LAUNCH_AUDIT_PLACEHOLDER",
        "provider": provider,
        "action": action,
        "decision": "PLAN_ONLY",
        "actor_placeholder": "OPERATOR_PLACEHOLDER",
        "timestamp_placeholder": "LAUNCH_AUDIT_TIMESTAMP_PLACEHOLDER",
        "raw_secret_logged": False,
        "provider_payload_redacted": True,
        "order_submitted": False,
        "account_read": False,
    }


def build_launch_audit_trail(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "external_log_upload": False,
        "events": [
            build_launch_audit_event(provider, "plan_review"),
            build_launch_audit_event(provider, "go_no_go_check"),
        ],
    }

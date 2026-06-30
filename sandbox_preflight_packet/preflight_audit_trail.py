from __future__ import annotations

from sandbox_preflight_packet.init import boundary


def build_preflight_audit_event(provider: str = "alpaca", action: str = "preflight_review") -> dict:
    return {
        **boundary(),
        "preflight_audit_id_placeholder": "PREFLIGHT_AUDIT_PLACEHOLDER",
        "provider": provider,
        "action": action,
        "decision": "NO_GO",
        "actor_placeholder": "OPERATOR_PLACEHOLDER",
        "timestamp_placeholder": "PREFLIGHT_TIMESTAMP_PLACEHOLDER",
        "raw_secret_logged": False,
        "provider_payload_redacted": True,
        "account_read": False,
        "order_submitted": False,
        "sandbox_api_called": False,
    }


def build_preflight_audit_trail(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "external_log_upload": False,
        "events": [
            build_preflight_audit_event(provider, "manifest_review"),
            build_preflight_audit_event(provider, "final_decision"),
        ],
    }

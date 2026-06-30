from __future__ import annotations

from sandbox_read_only_connector.init import boundary


def build_read_only_audit_event(provider: str = "alpaca", read_type: str = "account_snapshot") -> dict:
    return {
        **boundary(),
        "read_audit_ref_placeholder": "READ_AUDIT_REF_PLACEHOLDER",
        "provider": provider,
        "read_type": read_type,
        "account_ref_placeholder": "ACCOUNT_REF_REDACTED",
        "timestamp_placeholder": "TIMESTAMP_PLACEHOLDER",
        "actor_placeholder": "ACTOR_PLACEHOLDER",
        "raw_payload_stored": False,
        "provider_payload_redacted": True,
        "values_redacted": True,
        "order_submitted": False,
    }


def build_read_only_audit_policy(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "audit_policy": [
            "write one audit event per future read attempt",
            "store placeholder refs only",
            "redact provider payload",
            "redact values before frontend display",
            "never mark order submission true",
        ],
        "sample_event": build_read_only_audit_event(provider),
        "order_submitted": False,
    }

from __future__ import annotations

from sandbox_review_board.init import boundary


def build_review_audit_event(provider: str = "alpaca", action: str = "review") -> dict:
    return {
        **boundary(),
        "review_audit_id_placeholder": "REVIEW_AUDIT_PLACEHOLDER",
        "provider": provider,
        "action": action,
        "decision": "NO_GO",
        "actor_placeholder": "REVIEWER_PLACEHOLDER",
        "reviewer_role_placeholder": "REVIEWER_ROLE_PLACEHOLDER",
        "timestamp_placeholder": "REVIEW_TIMESTAMP_PLACEHOLDER",
        "raw_secret_logged": False,
        "provider_payload_redacted": True,
        "account_read": False,
        "order_submitted": False,
    }


def build_review_audit_trail(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "external_log_upload": False,
        "events": [
            build_review_audit_event(provider, "evidence_review"),
            build_review_audit_event(provider, "go_no_go_decision"),
        ],
    }

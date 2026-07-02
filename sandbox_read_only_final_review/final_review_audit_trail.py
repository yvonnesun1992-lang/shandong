from __future__ import annotations

from sandbox_read_only_final_review.init import boundary


def build_final_review_audit_event(provider: str = "alpaca", action: str = "review") -> dict:
    return {
        **boundary(),
        "final_review_audit_id_placeholder": "final_review_audit_id_placeholder",
        "provider": provider,
        "action": action,
        "decision": "READ_ONLY_FINAL_REVIEW_ONLY",
        "actor_placeholder": "reviewer_placeholder",
        "reviewer_role_placeholder": "security_reviewer_placeholder",
        "timestamp_placeholder": "timestamp_placeholder",
        "raw_secret_logged": False,
        "provider_payload_redacted": True,
        "account_read": False,
        "balance_read": False,
        "position_read": False,
        "order_submitted": False,
        "warnings": [],
    }


def build_final_review_audit_trail(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "events": [
            build_final_review_audit_event(provider, "charter_reviewed"),
            build_final_review_audit_event(provider, "evidence_reviewed"),
            build_final_review_audit_event(provider, "decision_recorded"),
        ],
        "warnings": [],
    }


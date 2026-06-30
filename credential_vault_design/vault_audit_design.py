from __future__ import annotations

from credential_vault_design import boundary


def build_vault_audit_design(provider: str) -> dict:
    return {
        "provider": provider,
        "audit_event_id_placeholder": "VAULT_AUDIT_EVENT_ID_PLACEHOLDER",
        "secret_reference_placeholder": "SECRET_REF_PLACEHOLDER",
        "actor": "vault_design_operator_placeholder",
        "action": "secret_access_design_review",
        "timestamp_placeholder": "TIMESTAMP_PLACEHOLDER",
        "approved_by_placeholder": "APPROVER_PLACEHOLDER",
        "reason": "design-only audit placeholder",
        "raw_secret_logged": False,
        "secret_value_redacted": True,
        **boundary(),
    }

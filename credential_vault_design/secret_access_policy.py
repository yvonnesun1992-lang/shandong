from __future__ import annotations

from credential_vault_design import boundary


def build_secret_access_policy() -> dict:
    roles = {
        "operator": {"access_enabled": False, "future_role": "approve_rotation_only"},
        "runtime_service": {"access_enabled": False, "future_role": "read_runtime_reference_only"},
        "audit_service": {"access_enabled": False, "future_role": "write_redacted_audit_only"},
        "emergency_revoke_operator": {"access_enabled": False, "future_role": "revoke_reference_only"},
        "frontend_user": {"access_enabled": False, "future_role": "no_access"},
    }
    return {"roles": roles, "all_access_disabled_in_v527": True, **boundary()}

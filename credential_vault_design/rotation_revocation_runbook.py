from __future__ import annotations

from credential_vault_design import boundary


def build_rotation_revocation_runbook(provider: str) -> dict:
    steps = [
        "scheduled rotation plan placeholder",
        "emergency revoke plan placeholder",
        "suspected leak procedure placeholder",
        "provider portal revoke placeholder",
        "vault update placeholder",
        "CI masked value update placeholder",
        "audit event placeholder",
        "operator confirmation placeholder",
    ]
    return {"provider": provider, "steps": steps, "provider_portal_access_enabled": False, "vault_runtime_enabled": False, **boundary()}

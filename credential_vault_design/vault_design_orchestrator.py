from __future__ import annotations

from credential_vault_design import boundary
from credential_vault_design.rotation_revocation_runbook import build_rotation_revocation_runbook
from credential_vault_design.secret_access_policy import build_secret_access_policy
from credential_vault_design.secret_scope_policy import build_secret_scope_policy
from credential_vault_design.vault_audit_design import build_vault_audit_design
from credential_vault_design.vault_interface_contract import get_secret_reference, validate_secret_reference
from credential_vault_design.vault_safety_validator import build_vault_safety_summary


def build_vault_design(provider: str) -> dict:
    reference = get_secret_reference(provider, "sandbox_read_only_key")
    return {
        "provider": provider,
        "interface": {"reference": reference, "validation": validate_secret_reference(reference)},
        "scope_policy": build_secret_scope_policy(),
        "access_policy": build_secret_access_policy(),
        "rotation_revocation": build_rotation_revocation_runbook(provider),
        "audit_design": build_vault_audit_design(provider),
        "safety": build_vault_safety_summary(),
        **boundary(),
    }


def summarize_vault_design(result: dict) -> dict:
    errors = [] if result["safety"]["safe"] else result["safety"]["errors"]
    warnings = ["vault interface is design-only; runtime remains disabled"]
    return {"provider": result["provider"], "warnings": warnings, "errors": errors, "verdict": "FAIL" if errors else "WARNING", **boundary()}

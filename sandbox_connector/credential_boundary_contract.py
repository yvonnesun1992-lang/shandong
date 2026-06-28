from __future__ import annotations

import json


BLOCKED = ["secret", "token=", "password=", "api_key=", "authorization:"]


def build_credential_boundary_contract() -> dict:
    return {
        "credentials_never_committed": True,
        "credentials_never_logged": True,
        "credentials_never_returned_to_frontend": True,
        "future_vault_runtime_only": True,
        "credential_handle_only": True,
        "plaintext_local_config_allowed": False,
        "ci_logs_masked": True,
        "contract_only": True,
    }


def validate_no_credentials(payload: dict) -> dict:
    text = json.dumps(payload, default=str).lower()
    errors = [term for term in BLOCKED if term in text]
    return {"valid": not errors, "errors": errors, "contract_only": True}

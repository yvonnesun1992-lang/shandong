from __future__ import annotations

import json


BLOCKED_CREDENTIAL_TERMS = ["secret", "token", "password", "api_key", "authorization"]


def build_credential_vault_blueprint() -> dict:
    return {
        "version": "V5.18",
        "blueprint_only": True,
        "future_vault_required": True,
        "repository_storage_allowed": False,
        "frontend_storage_allowed": False,
        "log_storage_allowed": False,
        "production_plaintext_env_allowed": False,
        "rotation_plan_required": True,
        "scope_separation_required": True,
        "sandbox_and_real_credentials_separate": True,
        "ci_masking_required": True,
        "emergency_revoke_required": True,
        "required_controls": [
            "no sensitive material in repository",
            "no sensitive material in frontend",
            "no sensitive material in logs",
            "vault-backed runtime injection for future operator",
            "credential rotation plan",
            "separate sandbox and real credential scopes",
            "CI masking",
            "emergency revoke procedure",
        ],
        "transition_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def validate_no_credentials_present(payload: object) -> dict:
    text = json.dumps(payload, default=str).lower()
    matches = [term for term in BLOCKED_CREDENTIAL_TERMS if term in text]
    return {
        "valid": not matches,
        "blocked": bool(matches),
        "reason": "sensitive credential marker present" if matches else "no credential markers present",
        "matches": ["redacted-marker" for _ in matches],
    }

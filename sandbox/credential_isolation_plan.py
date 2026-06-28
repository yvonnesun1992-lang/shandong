from __future__ import annotations


def build_credential_isolation_plan() -> dict:
    missing = [
        "external vault integration",
        "credential rotation runbook",
        "sandbox-only credential scope",
        "CI credential masking policy",
        "frontend credential exclusion tests",
    ]
    return {
        "credential_ready": False,
        "current_credentials_loaded": False,
        "plaintext_secret_allowed": False,
        "frontend_secret_exposure_allowed": False,
        "future_vault_required": True,
        "credentials_must_not_be_committed": True,
        "credentials_must_not_be_stored_plaintext": True,
        "credentials_must_not_be_logged": True,
        "credentials_loaded_from_external_vault_future": True,
        "local_env_future_placeholder_only": True,
        "ci_must_not_expose_credentials": True,
        "logs_must_be_sanitized": True,
        "frontend_never_receives_credentials": True,
        "sandbox_connection_enabled": False,
        "sandbox_orders_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "missing_requirements": missing,
    }

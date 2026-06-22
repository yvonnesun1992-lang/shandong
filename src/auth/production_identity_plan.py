from __future__ import annotations

from src.config.production_identity_config import (
    external_identity_mapping_ready,
    production_identity_enabled,
    production_session_lifecycle_ready,
)


def get_identity_mapping_checklist() -> list[str]:
    return [
        "choose identity provider",
        "define external subject mapping",
        "map external user to internal user_id",
        "map internal user to workspace membership",
        "define session expiry",
        "define logout and revocation",
        "define audit log retention",
        "define support account recovery",
    ]


def get_session_lifecycle_checklist() -> list[str]:
    return [
        "login",
        "refresh",
        "expiry",
        "logout",
        "revocation",
        "compromised session handling",
        "audit log",
        "support override policy",
    ]


def get_production_identity_integration_plan() -> dict:
    return {
        "current_identity": "demo_auth",
        "future_identity": "external_oidc_planned",
        "production_identity_enabled": production_identity_enabled(),
        "external_identity_connected": False,
        "external_identity_mapping_ready": external_identity_mapping_ready(),
        "production_session_lifecycle_ready": production_session_lifecycle_ready(),
        "auth_audit_ready": "planned",
        "identity_mapping_checklist": get_identity_mapping_checklist(),
        "session_lifecycle_checklist": get_session_lifecycle_checklist(),
        "warnings": [],
    }


def validate_identity_integration_boundary() -> dict:
    return {
        "valid": production_identity_enabled() is False,
        "production_identity_ready": False,
        "external_identity_connected": False,
        "warnings": [],
    }

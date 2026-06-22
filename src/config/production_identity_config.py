from __future__ import annotations

import os


def _normalized_env(name: str, default: str) -> str:
    return os.getenv(name, default).strip().lower() or default


def production_identity_mode() -> str:
    mode = _normalized_env("SHANDONG_PRODUCTION_IDENTITY_MODE", "demo")
    return mode if mode in {"demo", "planned", "production"} else "demo"


def production_identity_provider() -> str:
    provider = _normalized_env("SHANDONG_PRODUCTION_IDENTITY_PROVIDER", "demo")
    return provider if provider in {"demo", "oidc_planned", "enterprise_sso_planned"} else "demo"


def production_identity_enabled() -> bool:
    return _normalized_env("SHANDONG_ENABLE_PRODUCTION_IDENTITY", "false") == "true"


def external_identity_mapping_ready() -> bool:
    return _normalized_env("SHANDONG_EXTERNAL_IDENTITY_MAPPING_READY", "false") == "true"


def production_session_lifecycle_ready() -> bool:
    return _normalized_env("SHANDONG_PRODUCTION_SESSION_LIFECYCLE_READY", "false") == "true"


def production_identity_planning_status() -> dict:
    return {
        "mode": production_identity_mode(),
        "provider": production_identity_provider(),
        "production_identity_enabled": production_identity_enabled(),
        "external_identity_mapping_ready": external_identity_mapping_ready(),
        "production_session_lifecycle_ready": production_session_lifecycle_ready(),
        "external_identity_connected": False,
        "warnings": [],
    }

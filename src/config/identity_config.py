from __future__ import annotations

import os


VALID_IDENTITY_MODES = {"demo", "planned", "production"}
VALID_IDENTITY_PROVIDERS = {"demo", "external_planned"}


def _clean_choice(value: str | None, allowed: set[str], default: str) -> str:
    normalized = str(value or default).strip().lower()
    return normalized if normalized in allowed else default


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def identity_mode() -> str:
    return _clean_choice(os.getenv("SHANDONG_IDENTITY_MODE"), VALID_IDENTITY_MODES, "demo")


def identity_provider() -> str:
    mode = identity_mode()
    provider = _clean_choice(os.getenv("SHANDONG_IDENTITY_PROVIDER"), VALID_IDENTITY_PROVIDERS, "demo")
    if mode == "production" and provider != "external_planned":
        return "demo"
    return provider


def allow_demo_identity() -> bool:
    return _env_bool("SHANDONG_ALLOW_DEMO_IDENTITY", identity_mode() != "production")


def require_production_identity() -> bool:
    return _env_bool("SHANDONG_REQUIRE_PRODUCTION_IDENTITY", identity_mode() == "production")


def identity_planning_status() -> dict:
    mode = identity_mode()
    provider = identity_provider()
    warnings: list[str] = []
    if mode == "production":
        warnings.append("Production identity is planned but no external provider is enabled.")
    if provider == "external_planned":
        warnings.append("External identity provider is planned only.")

    return {
        "mode": mode,
        "provider": provider,
        "allow_demo_identity": allow_demo_identity(),
        "require_production_identity": require_production_identity(),
        "production_ready": False,
        "external_provider_enabled": False,
        "warnings": warnings,
    }

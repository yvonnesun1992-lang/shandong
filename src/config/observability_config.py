from __future__ import annotations

import os


VALID_OBSERVABILITY_MODES = {"local", "planned", "disabled"}
VALID_OBSERVABILITY_PROVIDERS = {"local", "external_planned"}


def _clean_choice(value: str | None, allowed: set[str], default: str) -> str:
    normalized = str(value or default).strip().lower()
    return normalized if normalized in allowed else default


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def observability_mode() -> str:
    return _clean_choice(os.getenv("SHANDONG_OBSERVABILITY_MODE"), VALID_OBSERVABILITY_MODES, "local")


def observability_provider() -> str:
    return _clean_choice(os.getenv("SHANDONG_OBSERVABILITY_PROVIDER"), VALID_OBSERVABILITY_PROVIDERS, "local")


def local_observability_enabled() -> bool:
    return _env_bool("SHANDONG_ENABLE_LOCAL_OBSERVABILITY", observability_mode() != "disabled")


def external_observability_enabled() -> bool:
    return _env_bool("SHANDONG_ENABLE_EXTERNAL_OBSERVABILITY", False)


def observability_planning_status() -> dict:
    mode = observability_mode()
    provider = observability_provider()
    warnings: list[str] = []
    if provider == "external_planned":
        warnings.append("External observability provider is planned only.")
    if external_observability_enabled():
        warnings.append("External observability flag is set, but this release keeps providers disabled.")
    return {
        "mode": mode,
        "provider": provider,
        "local_enabled": local_observability_enabled(),
        "external_provider_enabled": False,
        "warnings": warnings,
    }

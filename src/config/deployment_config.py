from __future__ import annotations

import os


VALID_DEPLOYMENT_MODES = {"local", "dry_run", "external_planned"}
VALID_DEPLOYMENT_TARGETS = {"local", "docker", "external_planned"}


def _clean_choice(value: str | None, allowed: set[str], default: str) -> str:
    normalized = str(value or default).strip().lower()
    return normalized if normalized in allowed else default


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def deployment_mode() -> str:
    return _clean_choice(os.getenv("SHANDONG_DEPLOYMENT_MODE"), VALID_DEPLOYMENT_MODES, "local")


def deployment_target() -> str:
    return _clean_choice(os.getenv("SHANDONG_DEPLOYMENT_TARGET"), VALID_DEPLOYMENT_TARGETS, "local")


def dry_run_enabled() -> bool:
    return _env_bool("SHANDONG_ENABLE_DEPLOYMENT_DRY_RUN", True)


def external_deployment_enabled() -> bool:
    return _env_bool("SHANDONG_ENABLE_EXTERNAL_DEPLOYMENT", False)


def deployment_planning_status() -> dict:
    warnings: list[str] = []
    if external_deployment_enabled():
        warnings.append("External deployment flag is set, but this release keeps launch disabled.")
    return {
        "mode": deployment_mode(),
        "target": deployment_target(),
        "dry_run_enabled": dry_run_enabled(),
        "external_deployment_enabled": False,
        "checks_available": True,
        "warnings": warnings,
    }

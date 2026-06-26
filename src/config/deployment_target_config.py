from __future__ import annotations

import os


def _normalized_env(name: str, default: str) -> str:
    return os.getenv(name, default).strip().lower() or default


def deployment_target_mode() -> str:
    mode = _normalized_env("SHANDONG_DEPLOYMENT_TARGET_MODE", "local")
    return mode if mode in {"local", "planned", "production"} else "local"


def frontend_target() -> str:
    target = _normalized_env("SHANDONG_FRONTEND_TARGET", "local")
    return target if target in {"local", "vercel_planned"} else "local"


def backend_target() -> str:
    target = _normalized_env("SHANDONG_BACKEND_TARGET", "local")
    return target if target in {"local", "render_planned", "flyio_planned"} else "local"


def database_target() -> str:
    target = _normalized_env("SHANDONG_DATABASE_TARGET", "local")
    return target if target in {"local", "postgres_planned"} else "local"


def secrets_target() -> str:
    target = _normalized_env("SHANDONG_SECRETS_TARGET", "local")
    return target if target in {"local", "secrets_manager_planned"} else "local"


def monitoring_target() -> str:
    target = _normalized_env("SHANDONG_MONITORING_TARGET", "local")
    return target if target in {"local", "sentry_planned", "opentelemetry_planned"} else "local"


def deployment_target_selection_status() -> dict:
    return {
        "deployment_target_mode": deployment_target_mode(),
        "frontend_target": frontend_target(),
        "backend_target": backend_target(),
        "database_target": database_target(),
        "secrets_target": secrets_target(),
        "monitoring_target": monitoring_target(),
        "production_deployment_enabled": False,
        "external_cloud_connected": False,
        "warnings": [],
    }

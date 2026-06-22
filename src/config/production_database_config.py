from __future__ import annotations

import os


def _normalized_env(name: str, default: str) -> str:
    return os.getenv(name, default).strip().lower() or default


def database_runtime_mode() -> str:
    mode = _normalized_env("SHANDONG_DATABASE_RUNTIME_MODE", "local")
    return mode if mode in {"local", "planned", "production"} else "local"


def production_database_provider() -> str:
    provider = _normalized_env("SHANDONG_DATABASE_PROVIDER", "sqlite")
    return provider if provider in {"sqlite", "postgres_planned"} else "sqlite"


def production_database_enabled() -> bool:
    return _normalized_env("SHANDONG_ENABLE_PRODUCTION_DATABASE", "false") == "true"


def database_migration_ready() -> bool:
    return _normalized_env("SHANDONG_DATABASE_MIGRATION_READY", "false") == "true"


def production_database_planning_status() -> dict:
    return {
        "runtime_mode": database_runtime_mode(),
        "provider": production_database_provider(),
        "production_enabled": production_database_enabled(),
        "migration_ready": database_migration_ready(),
        "connection_values_required": False,
        "external_database_connected": False,
        "warnings": [],
    }

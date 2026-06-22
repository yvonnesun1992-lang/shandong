from __future__ import annotations

from src.config.production_database_config import database_migration_ready, production_database_enabled


def get_database_migration_checklist() -> list[str]:
    return [
        "choose provider",
        "create production database",
        "configure protected config vault",
        "run migration in staging",
        "backup policy",
        "rollback policy",
        "retention policy",
    ]


def get_production_database_plan() -> dict:
    return {
        "current_database": "local_sqlite",
        "future_database": "postgres_planned",
        "production_enabled": production_database_enabled(),
        "migration_ready": database_migration_ready(),
        "sensitive_connection_values_required": False,
        "external_database_connected": False,
        "backup_policy_ready": False,
        "rollback_policy_ready": False,
        "checklist": get_database_migration_checklist(),
        "warnings": [],
    }


def validate_database_boundary() -> dict:
    return {
        "valid": production_database_enabled() is False,
        "production_database_ready": False,
        "external_database_connected": False,
        "warnings": [],
    }

from __future__ import annotations

from src.config import database_config
from src.db.repository import safe_identifier
from src.db.usage_repository import UsageRepository


def record_usage(
    workspace_id: str,
    user_id: str,
    event_type: str,
    quantity: int = 1,
    metadata: dict | list | str | None = None,
    database_url: str | None = None,
) -> dict:
    return UsageRepository(database_url or database_config.DATABASE_URL).add_usage_event(
        workspace_id=safe_identifier(workspace_id),
        user_id=safe_identifier(user_id),
        event_type=str(event_type or "unknown"),
        quantity=quantity,
        metadata=metadata,
    )


def get_daily_usage(workspace_id: str, event_type: str, database_url: str | None = None) -> int:
    return UsageRepository(database_url or database_config.DATABASE_URL).get_daily_usage(
        safe_identifier(workspace_id),
        str(event_type or "unknown"),
    )


def get_usage_summary(workspace_id: str, database_url: str | None = None) -> dict:
    safe_workspace = safe_identifier(workspace_id)
    return {
        "workspace_id": safe_workspace,
        "report_generate": get_daily_usage(safe_workspace, "report_generate", database_url=database_url),
        "api_call": get_daily_usage(safe_workspace, "api_call", database_url=database_url),
        "auth_login": get_daily_usage(safe_workspace, "auth_login", database_url=database_url),
    }

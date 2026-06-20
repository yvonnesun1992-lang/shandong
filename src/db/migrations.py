from __future__ import annotations

from src.config.database_config import DATABASE_URL
from src.db.models import CREATE_TABLES_SQL
from src.db.session import get_connection


WORKSPACE_COLUMNS = {
    "users": "workspace_id text not null default 'default'",
    "strategy_reports": "workspace_id text not null default 'default'",
    "api_keys": "workspace_id text not null default 'default'",
    "billing_plans": "workspace_id text not null default 'default'",
    "audit_logs": "workspace_id text not null default 'default'",
    "user_sessions": "workspace_id text not null default 'default'",
    "user_permissions": "workspace_id text not null default 'default'",
}


def _table_columns(connection, table_name: str) -> set[str]:
    rows = connection.execute(f"pragma table_info({table_name})").fetchall()
    return {str(row["name"]) for row in rows}


def _ensure_workspace_columns(connection) -> int:
    added = 0
    for table_name, column_sql in WORKSPACE_COLUMNS.items():
        columns = _table_columns(connection, table_name)
        if columns and "workspace_id" not in columns:
            connection.execute(f"alter table {table_name} add column {column_sql}")
            added += 1
        if columns or "workspace_id" in _table_columns(connection, table_name):
            connection.execute(f"update {table_name} set workspace_id = 'default' where workspace_id is null or workspace_id = ''")
    return added


def initialize_database(database_url: str | None = None) -> dict:
    url = database_url or DATABASE_URL
    with get_connection(url) as connection:
        for statement in CREATE_TABLES_SQL:
            connection.execute(statement)
        workspace_columns_added = _ensure_workspace_columns(connection)
    return {"status": "ok", "database_url": url, "tables": len(CREATE_TABLES_SQL), "workspace_columns_added": workspace_columns_added}

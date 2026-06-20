from __future__ import annotations

from src.config.database_config import DATABASE_URL
from src.db.models import CREATE_TABLES_SQL
from src.db.session import get_connection


def initialize_database(database_url: str | None = None) -> dict:
    url = database_url or DATABASE_URL
    with get_connection(url) as connection:
        for statement in CREATE_TABLES_SQL:
            connection.execute(statement)
    return {"status": "ok", "database_url": url, "tables": len(CREATE_TABLES_SQL)}

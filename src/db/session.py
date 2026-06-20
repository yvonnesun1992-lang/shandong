from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from src.config.database_config import DATABASE_URL
from src.db.base import connect_sqlite


@contextmanager
def get_connection(database_url: str | None = None) -> Iterator:
    connection = connect_sqlite(database_url or DATABASE_URL)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

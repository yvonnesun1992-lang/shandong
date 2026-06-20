from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.config.database_config import DATABASE_URL, ensure_database_parent


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def encode_json(value: Any) -> str:
    if value is None:
        return "{}"
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def decode_json(value: str | bytes | None) -> dict | list:
    if not value:
        return {}
    try:
        decoded = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return {}
    return decoded if isinstance(decoded, (dict, list)) else {}


def connect_sqlite(database_url: str | None = None) -> sqlite3.Connection:
    path = ensure_database_parent(database_url or DATABASE_URL)
    connection = sqlite3.connect(Path(path), timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("pragma foreign_keys = on")
    return connection

from __future__ import annotations

import os
from pathlib import Path


DEFAULT_DATABASE_URL = "sqlite:///data/shandong_v2.db"
DATABASE_URL = os.getenv("SHANDONG_DATABASE_URL", DEFAULT_DATABASE_URL)
USE_DATABASE_STORAGE = os.getenv("SHANDONG_USE_DATABASE_STORAGE", "true").strip().lower() in {"1", "true", "yes", "on"}
DB_ECHO = os.getenv("SHANDONG_DB_ECHO", "false").strip().lower() in {"1", "true", "yes", "on"}


def sqlite_path_from_url(database_url: str | None = None) -> Path:
    url = str(database_url or DATABASE_URL)
    if not url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported by the local database foundation")
    raw_path = url.removeprefix("sqlite:///")
    if not raw_path:
        raise ValueError("SQLite database URL must include a path")
    return Path(raw_path).expanduser()


def ensure_database_parent(database_url: str | None = None) -> Path:
    path = sqlite_path_from_url(database_url)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


ensure_database_parent(DATABASE_URL)

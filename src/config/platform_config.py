from __future__ import annotations

import os


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


CACHE_ENABLED = _env_bool("SHANDONG_CACHE_ENABLED", True)
API_ENABLED = _env_bool("SHANDONG_API_ENABLED", True)
MULTI_USER = _env_bool("SHANDONG_MULTI_USER", True)
LOG_LEVEL = os.getenv("SHANDONG_LOG_LEVEL", "INFO").strip().upper() or "INFO"
PLATFORM_VERSION = "V1.32"

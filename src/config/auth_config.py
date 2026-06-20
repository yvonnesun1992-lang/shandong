from __future__ import annotations

import os


VALID_AUTH_MODES = {"local", "dev", "production"}


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def auth_mode() -> str:
    mode = os.getenv("SHANDONG_AUTH_MODE", "local").strip().lower()
    return mode if mode in VALID_AUTH_MODES else "local"


def require_auth() -> bool:
    return _bool_env("SHANDONG_REQUIRE_AUTH", auth_mode() == "production")


def allow_local_admin_fallback() -> bool:
    return _bool_env("SHANDONG_ALLOW_LOCAL_ADMIN_FALLBACK", auth_mode() == "local")


def session_ttl_minutes() -> int:
    return max(_int_env("SHANDONG_SESSION_TTL_MINUTES", 240), 1)


def api_key_required_for_production() -> bool:
    return _bool_env("SHANDONG_API_KEY_REQUIRED_FOR_PRODUCTION", auth_mode() == "production")


SHANDONG_AUTH_MODE = auth_mode()
SHANDONG_REQUIRE_AUTH = require_auth()
SHANDONG_ALLOW_LOCAL_ADMIN_FALLBACK = allow_local_admin_fallback()
SHANDONG_SESSION_TTL_MINUTES = session_ttl_minutes()
SHANDONG_API_KEY_REQUIRED_FOR_PRODUCTION = api_key_required_for_production()

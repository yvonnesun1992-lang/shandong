from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from src.config import database_config
from src.db.repository import UserSessionRepository, safe_identifier


def hash_session_value(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def create_session(user_id: str, ttl_minutes: int = 240, metadata: dict | None = None) -> dict:
    safe_user = safe_identifier(user_id)
    session_value = secrets.token_urlsafe(32)
    expires_at = (datetime.now(UTC) + timedelta(minutes=max(int(ttl_minutes or 240), 1))).replace(microsecond=0).isoformat()
    UserSessionRepository(database_config.DATABASE_URL).create_session_record(
        user_id=safe_user,
        session_id_hash=hash_session_value(session_value),
        expires_at=expires_at,
        metadata=metadata or {},
    )
    return {"session_id": session_value, "user_id": safe_user, "status": "active", "expires_at": expires_at}


def get_session(session_id: str) -> dict | None:
    record = UserSessionRepository(database_config.DATABASE_URL).get_session_by_hash(hash_session_value(session_id))
    if record is None:
        return None
    return record


def revoke_session(session_id: str) -> bool:
    return UserSessionRepository(database_config.DATABASE_URL).revoke_session_by_hash(hash_session_value(session_id))


def is_session_active(session_id: str) -> bool:
    record = get_session(session_id)
    if record is None:
        return False
    if record.get("status") != "active":
        return False
    expires_at = _parse_time(record.get("expires_at"))
    if expires_at is None:
        return False
    if expires_at <= datetime.now(UTC):
        return False
    UserSessionRepository(database_config.DATABASE_URL).touch_session_by_hash(hash_session_value(session_id))
    return True

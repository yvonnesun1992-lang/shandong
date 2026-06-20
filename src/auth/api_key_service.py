from __future__ import annotations

import hashlib

from src.config import database_config
from src.db.repository import ApiKeyRepository, safe_identifier


def hash_api_key(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def create_api_key(user_id: str, key_id: str, raw_key: str) -> dict:
    safe_user = safe_identifier(user_id)
    safe_key = safe_identifier(key_id, "key")
    ApiKeyRepository(database_config.DATABASE_URL).create_api_key_record(
        user_id=safe_user,
        key_id=safe_key,
        key_hash=hash_api_key(raw_key),
    )
    return {"user_id": safe_user, "key_id": safe_key, "raw_key": raw_key}


def verify_api_key(user_id: str, raw_key: str) -> bool:
    safe_user = safe_identifier(user_id)
    raw_hash = hash_api_key(raw_key)
    records = ApiKeyRepository(database_config.DATABASE_URL).list_api_keys_by_user(safe_user)
    return any(record.get("status") == "active" and record.get("key_hash") == raw_hash for record in records)


def revoke_api_key(user_id: str, key_id: str) -> bool:
    return ApiKeyRepository(database_config.DATABASE_URL).revoke_api_key(key_id, user_id=safe_identifier(user_id))

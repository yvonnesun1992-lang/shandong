from __future__ import annotations

import hashlib
from dataclasses import dataclass

from src.auth import User


@dataclass
class ApiKeyRecord:
    key_id: str
    key_value: str
    user_id: str
    label: str
    active: bool = True
    usage_count: int = 0

    def public_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "user_id": self.user_id,
            "label": self.label,
            "active": self.active,
            "usage_count": self.usage_count,
        }


class ApiKeyManager:
    def __init__(self, rate_limit: int = 100) -> None:
        self.rate_limit = max(int(rate_limit), 1)
        self._records: dict[str, ApiKeyRecord] = {}
        self._by_value: dict[str, str] = {}

    def generate_key(self, user: User, label: str = "default") -> ApiKeyRecord:
        seed = f"{user.user_id}:{label}:{len(self._records) + 1}"
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        key_id = f"mock_{digest[:12]}"
        key_value = f"mock_key_{digest[12:36]}"
        record = ApiKeyRecord(key_id=key_id, key_value=key_value, user_id=user.user_id, label=label)
        self._records[key_id] = record
        self._by_value[key_value] = key_id
        return record

    def authenticate(self, key_value: str) -> dict:
        record = self._record_for_value(key_value)
        if record is None or not record.active:
            return {"allowed": False, "reason": "invalid_key", "record": None}
        return {"allowed": True, "reason": "ok", "record": record.public_dict()}

    def track_usage(self, key_value: str) -> dict:
        record = self._record_for_value(key_value)
        if record is None or not record.active:
            return {"allowed": False, "reason": "invalid_key"}
        if record.usage_count >= self.rate_limit:
            return {"allowed": False, "reason": "rate_limit_exceeded", "usage_count": record.usage_count}
        record.usage_count += 1
        return {"allowed": True, "reason": "ok", "usage_count": record.usage_count}

    def revoke_key(self, key_id: str) -> bool:
        record = self._records.get(key_id)
        if record is None:
            return False
        record.active = False
        return True

    def _record_for_value(self, key_value: str) -> ApiKeyRecord | None:
        key_id = self._by_value.get(str(key_value))
        if key_id is None:
            return None
        return self._records.get(key_id)

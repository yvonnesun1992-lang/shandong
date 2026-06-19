from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float
    created_at: float


def build_cache_key(strategy: str, watchlist: str, preset: str, params: dict | None = None) -> str:
    """Build a stable cache key from strategy, watchlist, preset, and parameters."""
    payload = {
        "strategy": str(strategy or "").strip(),
        "watchlist": str(watchlist or "").strip(),
        "preset": str(preset or "").strip(),
        "params": params or {},
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{payload['strategy']}:{payload['watchlist']}:{payload['preset']}:{digest}"


class StrategyCacheManager:
    """Small in-memory TTL cache for local strategy research results."""

    def __init__(self, default_ttl_seconds: int = 900) -> None:
        self.default_ttl_seconds = max(int(default_ttl_seconds), 1)
        self._store: dict[str, CacheEntry] = {}
        self._hit_count = 0
        self._miss_count = 0
        self._expired_count = 0

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        ttl = self.default_ttl_seconds if ttl_seconds is None else max(int(ttl_seconds), 1)
        now = time.time()
        self._store[str(key)] = CacheEntry(value=value, expires_at=now + ttl, created_at=now)

    def get(self, key: str) -> Any | None:
        clean_key = str(key)
        entry = self._store.get(clean_key)
        if entry is None:
            self._miss_count += 1
            return None
        if entry.expires_at < time.time():
            self._expired_count += 1
            self._miss_count += 1
            self._store.pop(clean_key, None)
            return None
        self._hit_count += 1
        return entry.value

    def clear(self) -> None:
        self._store.clear()
        self._hit_count = 0
        self._miss_count = 0
        self._expired_count = 0

    def stats(self) -> dict:
        total = self._hit_count + self._miss_count
        hit_rate = self._hit_count / total if total else 0.0
        return {
            "cache_size": len(self._store),
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "expired_count": self._expired_count,
            "hit_rate": hit_rate,
        }

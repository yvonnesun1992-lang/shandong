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
        self._context: dict[str, str] = {}
        self._hit_count = 0
        self._miss_count = 0
        self._expired_count = 0

    def update_context(self, strategy: str, watchlist: str, preset: str) -> None:
        next_context = {
            "strategy": str(strategy or "").strip(),
            "watchlist": str(watchlist or "").strip(),
            "preset": str(preset or "").strip(),
        }
        if self._context and self._context != next_context:
            self.invalidate()
        self._context = next_context

    def invalidate(self) -> None:
        self._store.clear()

    def invalidate_for_context(self, strategy: str | None = None, watchlist: str | None = None, preset: str | None = None) -> None:
        checks = {
            "strategy": strategy,
            "watchlist": watchlist,
            "preset": preset,
        }
        for key, value in checks.items():
            if value is not None and self._context.get(key) != str(value).strip():
                self.invalidate()
                return

    def _typed_key(self, kind: str, key: str) -> str:
        return f"{kind}:{key}"

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

    def set_report(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        self.set(self._typed_key("report", key), value, ttl_seconds)

    def get_report(self, key: str) -> Any | None:
        return self.get(self._typed_key("report", key))

    def set_dashboard(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        self.set(self._typed_key("dashboard", key), value, ttl_seconds)

    def get_dashboard(self, key: str) -> Any | None:
        return self.get(self._typed_key("dashboard", key))

    def set_compare(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        self.set(self._typed_key("compare", key), value, ttl_seconds)

    def get_compare(self, key: str) -> Any | None:
        return self.get(self._typed_key("compare", key))

    def set_trend(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        self.set(self._typed_key("trend", key), value, ttl_seconds)

    def get_trend(self, key: str) -> Any | None:
        return self.get(self._typed_key("trend", key))

    def clear(self) -> None:
        self._store.clear()
        self._context = {}
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

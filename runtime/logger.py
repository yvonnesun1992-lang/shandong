from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


SENSITIVE_KEYS = {"api_key", "secret", "token", "password", "authorization"}


class ProductionLogger:
    def __init__(self, path: str | Path = "logs/runtime.jsonl") -> None:
        self.path = Path(path)

    def log(self, event_type: str, payload: dict | None = None) -> dict:
        record = {
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "event_type": str(event_type),
            "payload": _sanitize(payload or {}),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return record


def _sanitize(value):
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]" if str(key).lower() in SENSITIVE_KEYS else _sanitize(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


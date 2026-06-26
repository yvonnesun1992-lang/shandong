from __future__ import annotations

import json
import time
from datetime import datetime, UTC
from pathlib import Path


class StateCheckpoint:
    def __init__(self, path: str | Path = "data/runtime_state_checkpoint.json", interval_seconds: float = 30.0) -> None:
        self.path = Path(path)
        self.interval_seconds = float(interval_seconds)
        self.last_saved_at = 0.0

    def should_save(self) -> bool:
        return (time.monotonic() - self.last_saved_at) >= self.interval_seconds

    def save(self, state: dict, force: bool = False) -> Path:
        if not force and not self.should_save():
            return self.path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = _json_safe(state)
        payload["checkpoint_saved_at"] = datetime.now(UTC).replace(microsecond=0).isoformat()
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.last_saved_at = time.monotonic()
        return self.path

    def load_latest(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))


def _json_safe(value):
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


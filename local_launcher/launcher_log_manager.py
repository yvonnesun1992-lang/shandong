from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

from local_launcher.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SENSITIVE_KEY_PATTERN = re.compile(r"(secret|token|password|api[_-]?key|raw[_-]?key|session[_-]?id|authorization|account[_-]?id|order[_-]?id)", re.IGNORECASE)


def get_launcher_log_dir() -> Path:
    configured = os.getenv("SHANDONG_V5_LOCAL_LAUNCHER_LOG_DIR")
    if configured:
        return Path(configured)
    return PROJECT_ROOT / "reports" / "local_launcher"


def _sanitize(value):
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            if SENSITIVE_KEY_PATTERN.search(str(key)):
                continue
            clean[key] = _sanitize(item)
        return clean
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, str):
        text = SENSITIVE_KEY_PATTERN.sub("redacted", value)
        return text.replace(str(PROJECT_ROOT), "<project>")
    return value


def build_launcher_log_event(action: str, status: str, details: dict | None = None) -> dict:
    return {
        "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "action": action,
        "status": status,
        "details": _sanitize(details or {}),
        **boundary(),
    }


def write_launcher_log(event: dict) -> dict:
    if "timestamp" not in event:
        event = build_launcher_log_event(str(event.get("action", "unknown")), str(event.get("status", "unknown")), event.get("details", {}))
    event = _sanitize(event)
    log_dir = get_launcher_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    filename = f"local_launcher_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.json"
    (log_dir / filename).write_text(json.dumps(event, ensure_ascii=False, indent=2), encoding="utf-8")
    return event


def read_recent_launcher_logs(limit: int = 20) -> list[dict]:
    log_dir = get_launcher_log_dir()
    if not log_dir.exists():
        return []
    logs = []
    for path in sorted(log_dir.glob("local_launcher_*.json"), reverse=True)[:limit]:
        try:
            logs.append(_sanitize(json.loads(path.read_text(encoding="utf-8"))))
        except Exception:
            logs.append(build_launcher_log_event("read_log", "warning", {"file": path.name}))
    return logs

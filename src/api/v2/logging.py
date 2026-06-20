from __future__ import annotations

import logging
from typing import Any

from src.config import database_config
from src.db.repository import AuditLogRepository, safe_identifier


LOGGER = logging.getLogger("shandong.api.v2")
SENSITIVE_FIELDS = {"secret", "token", "password", "api_key", "apikey", "raw_api_key", "key_value"}


def sanitize_log_value(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_FIELDS:
                clean[str(key)] = "[redacted]"
                continue
            clean[str(key)] = sanitize_log_value(item)
        return clean
    if isinstance(value, list):
        return [sanitize_log_value(item) for item in value]
    text = str(value)
    for marker in SENSITIVE_FIELDS:
        if marker in text.lower():
            return "[redacted]"
    return value


def log_api_event(
    endpoint: str,
    user_id: str,
    status: str,
    latency_ms: float,
    warning_count: int = 0,
    metadata: dict | None = None,
) -> dict:
    safe_user = safe_identifier(user_id)
    event = {
        "endpoint": str(endpoint),
        "user_id": safe_user,
        "status": str(status),
        "latency_ms": round(float(latency_ms or 0), 2),
        "warning_count": int(warning_count or 0),
        "metadata": sanitize_log_value(metadata or {}),
    }
    try:
        AuditLogRepository(database_config.DATABASE_URL).add_log(
            user_id=safe_user,
            action=f"api.{event['status']}",
            resource_type="api",
            resource_id=event["endpoint"],
            metadata=event,
        )
        event["logged"] = True
    except Exception as exc:
        LOGGER.info("api_event_fallback", extra={"event": event, "error_type": type(exc).__name__})
        event["logged"] = False
    return event

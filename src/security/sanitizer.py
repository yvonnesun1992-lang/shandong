from __future__ import annotations

import re
from typing import Any


SENSITIVE_KEYS = {"secret", "token", "password", "api_key", "raw_key", "session_id", "bearer", "authorization"}
PATH_PATTERN = re.compile(r"(/[^\s:,}]+)+")
DB_FILE_PATTERN = re.compile(r"\b[\w.-]+\.db\b", re.IGNORECASE)
ASSIGNMENT_PATTERN = re.compile(
    r"(secret|token|password|api[_-]?key|raw_key|session_id|authorization|bearer)\s*=\s*[^\s,}]+",
    re.IGNORECASE,
)


def sanitize_sensitive_value(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            key_text = str(key)
            normalized_key = key_text.lower()
            if normalized_key in SENSITIVE_KEYS or any(marker in normalized_key for marker in SENSITIVE_KEYS):
                continue
            clean[key_text] = sanitize_sensitive_value(item)
        return clean
    if isinstance(value, list):
        return [sanitize_sensitive_value(item) for item in value]
    if not isinstance(value, str):
        return value
    text = ASSIGNMENT_PATTERN.sub("[redacted]", value)
    text = PATH_PATTERN.sub("[path]", text)
    text = DB_FILE_PATTERN.sub("[database]", text)
    for marker in SENSITIVE_KEYS:
        text = re.sub(re.escape(marker), "[redacted]", text, flags=re.IGNORECASE)
    return text


def sanitize_response_payload(payload: Any) -> Any:
    return sanitize_sensitive_value(payload)


def sanitize_exception_message(message: str) -> str:
    sanitized = sanitize_sensitive_value(str(message))
    return sanitized if isinstance(sanitized, str) else "sanitized error"

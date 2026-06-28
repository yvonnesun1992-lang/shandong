from __future__ import annotations

from sandbox_bridge.sanitizer import bridge_boundary, sanitize_bridge_payload


ERROR_MAP = {
    "timeout": "TIMEOUT",
    "rate limit": "RATE_LIMITED",
    "auth error": "CREDENTIAL_INVALID",
    "credential": "CREDENTIAL_INVALID",
    "order rejected": "ORDER_REJECTED",
    "rejected": "ORDER_REJECTED",
}


def translate_error(error: dict | str) -> dict:
    clean = sanitize_bridge_payload(error)
    text = str(clean).lower()
    code = "UNKNOWN_ERROR"
    for marker, mapped in ERROR_MAP.items():
        if marker in text:
            code = mapped
            break
    return {
        "error_code": code,
        "message": "bridge sanitized error",
        "raw_error_available": False,
        **bridge_boundary(),
    }

from __future__ import annotations

import json

from sandbox_bridge.sanitizer import bridge_boundary


BLOCKED_MARKERS = ("api_key=", "secret=", "token=", "password=", "authorization:", "oauth", "sandbox_api_url", "https://sandbox")


def validate_bridge_safety(config: dict | None = None) -> dict:
    config = config or {}
    text = json.dumps(config, default=str).lower()
    errors = []
    if config.get("real_connection") is True:
        errors.append("real connection blocked")
    if config.get("network_call_attempted") is True:
        errors.append("network call blocked")
    if any(marker in text for marker in BLOCKED_MARKERS):
        errors.append("blocked bridge runtime config")
    return {
        "safe": not errors,
        "errors": errors,
        "blocked_real_connection": True,
        "reason": "V5.16 sandbox bridge only",
        **bridge_boundary(),
    }

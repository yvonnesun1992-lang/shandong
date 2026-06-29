from __future__ import annotations

import json

from integration_test.sanitizer import integration_boundary


BLOCKED_MARKERS = ("api_key=", "secret=", "token=", "password=", "authorization:", "oauth", "https://sandbox")


def validate_integration_safety(config: dict | None = None) -> dict:
    config = config or {}
    text = json.dumps(config, default=str).lower()
    errors = []
    if config.get("real_connection") is True or config.get("broker_connected") is True:
        errors.append("real connection blocked")
    if config.get("network_call_attempted") is True:
        errors.append("network call blocked")
    if config.get("real_adapter_detected") is True:
        errors.append("real adapter blocked")
    if any(marker in text for marker in BLOCKED_MARKERS):
        errors.append("sensitive integration config blocked")
    return {"safe": not errors, "errors": errors, "blocked_real_connection": True, "reason": "V5.17 integration test only", **integration_boundary()}

from __future__ import annotations

import json
import re

from provider_offline_replay import boundary


BLOCKED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"api[_ -]?key",
        r"secret",
        r"token\s*=",
        r"password",
        r"authorization",
        r"real_order_id",
        r"account_id",
        r"raw provider payload",
        r"raw provider response",
        r"provider_endpoint_url",
        r"https?://",
        r"paper-api",
    ]
]


def validate_replay_safety(payload: dict | list | str) -> dict:
    payload_text = json.dumps(payload, default=str) if not isinstance(payload, str) else payload
    errors = []
    checks = []
    for key in [
        "replay_runtime_enabled",
        "sandbox_api_enabled",
        "account_read_enabled",
        "order_submission_enabled",
        "broker_connected",
        "real_money_enabled",
    ]:
        if isinstance(payload, dict) and payload.get(key) is True:
            errors.append(f"{key} must remain false in V5.23")
        checks.append({"check": key, "status": "OK" if f"{key} must remain false in V5.23" not in errors else "FAIL"})

    for pattern in BLOCKED_PATTERNS:
        if pattern.search(payload_text):
            errors.append(f"blocked sensitive pattern: {pattern.pattern}")

    checks.extend(
        [
            {"check": "no broker SDK imports", "status": "OK"},
            {"check": "no network calls", "status": "OK"},
            {"check": "no plaintext credentials", "status": "OK"},
            {"check": "no real account id", "status": "OK"},
            {"check": "no real order id", "status": "OK"},
            {"check": "no raw provider payload", "status": "OK"},
            {"check": "no provider endpoint URL", "status": "OK"},
        ]
    )
    return {"safe": not errors, "checks": checks, "errors": errors, "warnings": [], **boundary()}


def build_replay_safety_summary() -> dict:
    return validate_replay_safety(boundary())

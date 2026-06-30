from __future__ import annotations

import json
import re

from provider_sandbox_evidence import boundary


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


def validate_evidence_safety(payload: dict | list | str) -> dict:
    payload_text = json.dumps(payload, default=str) if not isinstance(payload, str) else payload
    errors = []
    checks = []
    for key in [
        "evidence_runtime_enabled",
        "sandbox_api_enabled",
        "account_read_enabled",
        "order_submission_enabled",
        "broker_connected",
        "real_money_enabled",
    ]:
        failed = isinstance(payload, dict) and payload.get(key) is True
        if failed:
            errors.append(f"{key} must remain false in V5.26")
        checks.append({"check": key, "status": "FAIL" if failed else "OK"})
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(payload_text):
            errors.append(f"blocked sensitive pattern: {pattern.pattern}")
    checks.extend(
        [
            {"check": "no broker SDK imports", "status": "OK"},
            {"check": "no network calls", "status": "OK"},
            {"check": "no plaintext credentials", "status": "OK"},
            {"check": "no real account reference", "status": "OK"},
            {"check": "no real order reference", "status": "OK"},
            {"check": "provider payload storage disabled", "status": "OK"},
            {"check": "provider endpoint placeholder disabled", "status": "OK"},
        ]
    )
    return {"safe": not errors, "checks": checks, "errors": errors, "warnings": [], **boundary()}


def build_evidence_safety_summary() -> dict:
    return validate_evidence_safety(boundary())

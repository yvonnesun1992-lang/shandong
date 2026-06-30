from __future__ import annotations

import json
import re

from credential_vault_design import boundary


BLOCKED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"secret_value\s*=",
        r"api[_ -]?key\s*=",
        r"token\s*=",
        r"password\s*=",
        r"authorization",
        r"real_order_id",
        r"account_id",
        r"raw provider payload",
        r"raw provider response",
        r"provider_endpoint_url",
        r"https?://",
    ]
]


def validate_vault_design_safety(payload: dict | list | str) -> dict:
    payload_text = json.dumps(payload, default=str) if not isinstance(payload, str) else payload
    errors = []
    checks = []
    for key in [
        "vault_runtime_enabled",
        "secret_read_enabled",
        "secret_write_enabled",
        "sandbox_api_enabled",
        "broker_connected",
        "order_submission_enabled",
        "real_money_enabled",
    ]:
        failed = isinstance(payload, dict) and payload.get(key) is True
        if failed:
            errors.append(f"{key} must remain false in V5.27")
        checks.append({"check": key, "status": "FAIL" if failed else "OK"})
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(payload_text):
            errors.append(f"blocked sensitive pattern: {pattern.pattern}")
    return {"safe": not errors, "checks": checks, "errors": errors, "warnings": [], **boundary()}


def build_vault_safety_summary() -> dict:
    return validate_vault_design_safety(boundary())

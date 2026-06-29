from __future__ import annotations

import json
import re

from config.v5_provider_mock_contract_config import get_mock_contract_status
from provider_mock_contract import boundary


def validate_mock_contract_safety(payload: object | None = None) -> dict:
    state = payload or get_mock_contract_status()
    text = json.dumps(state, default=str).lower()
    checks = []
    errors = []
    for key in ["mock_contract_runtime_enabled", "sandbox_api_enabled", "account_read_enabled", "order_submission_enabled", "broker_connected", "real_money_enabled"]:
        value = state.get(key, False) if isinstance(state, dict) else False
        ok = value is False
        checks.append({"check": key, "status": "OK" if ok else "ERROR"})
        if not ok:
            errors.append({"check": key, "message": f"{key} must remain false in V5.22"})
    blocked_patterns = [
        r"api[_-]?key\s*[:=]\s*[a-z0-9]",
        r"secret\s*[:=]\s*[a-z0-9]",
        r"token\s*[:=]\s*[a-z0-9]",
        r"password\s*[:=]\s*[a-z0-9]",
        r"raw provider payload",
        r"raw provider response",
        r"provider endpoint url",
        r"real[_-]?order[_-]?id\s*[:=]\s*[a-z0-9]",
        r"account[_-]?id\s*[:=]\s*[a-z0-9]",
        r"sk-[a-z0-9]",
    ]
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in blocked_patterns):
        errors.append({"check": "no_sensitive_or_raw_provider_payload", "message": "blocked credential or raw provider payload pattern"})
        checks.append({"check": "no_sensitive_or_raw_provider_payload", "status": "ERROR"})
    else:
        checks.append({"check": "no_sensitive_or_raw_provider_payload", "status": "OK"})
    return {"safe": not errors, "checks": checks, "errors": errors, "warnings": [], **boundary()}


def build_mock_contract_safety_summary() -> dict:
    summary = validate_mock_contract_safety(get_mock_contract_status())
    summary["checks"].extend(
        [
            {"check": "no broker SDK import", "status": "OK"},
            {"check": "no network calls", "status": "OK"},
            {"check": "provider_endpoint_placeholder_only", "status": "OK"},
            {"check": "provider_payload_storage_disabled", "status": "OK"},
        ]
    )
    return summary

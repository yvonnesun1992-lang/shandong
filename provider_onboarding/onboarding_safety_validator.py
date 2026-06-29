from __future__ import annotations

import json
import re

from config.v5_provider_onboarding_config import get_onboarding_status
from provider_onboarding import boundary


def validate_no_portal_access(payload: dict | None = None) -> dict:
    value = (payload or get_onboarding_status()).get("provider_portal_access_enabled", False)
    return _check_false("provider_portal_access_enabled", value)


def validate_no_api_key_creation(payload: dict | None = None) -> dict:
    value = (payload or get_onboarding_status()).get("api_key_creation_enabled", False)
    return _check_false("api_key_creation_enabled", value)


def validate_no_sandbox_connection(payload: dict | None = None) -> dict:
    value = (payload or get_onboarding_status()).get("sandbox_api_enabled", False)
    return _check_false("sandbox_api_enabled", value)


def validate_no_credentials(payload: object) -> dict:
    text = json.dumps(payload, default=str).lower()
    patterns = [
        r"api[_-]?key\s*[:=]\s*[a-z0-9]",
        r"secret\s*[:=]\s*[a-z0-9]",
        r"token\s*[:=]\s*[a-z0-9]",
        r"password\s*[:=]\s*[a-z0-9]",
        r"authorization\s*[:=]\s*[a-z0-9]",
        r"account[_-]?id\s*[:=]\s*[a-z0-9]",
        r"real[_-]?order[_-]?id\s*[:=]\s*[a-z0-9]",
        r"sk-[a-z0-9]",
        r"-----begin",
    ]
    errors = [{"check": "no_plaintext_credentials", "status": "ERROR"}] if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns) else []
    return {"safe": not errors, "checks": [{"check": "no_plaintext_credentials", "status": "OK" if not errors else "ERROR"}], "warnings": [], "errors": errors, **boundary()}


def validate_onboarding_safety(payload: dict | None = None) -> dict:
    state = payload or get_onboarding_status()
    checks = [
        validate_no_portal_access(state),
        validate_no_api_key_creation(state),
        validate_no_sandbox_connection(state),
        _check_false("broker_connected", state.get("broker_connected", False)),
        _check_false("real_orders_enabled", state.get("real_orders_enabled", False)),
        _check_false("real_money_enabled", state.get("real_money_enabled", False)),
        validate_no_credentials(state),
    ]
    errors = [error for check in checks for error in check["errors"]]
    warnings = [warning for check in checks for warning in check["warnings"]]
    return {
        "safe": not errors,
        "checks": [item for check in checks for item in check["checks"]],
        "warnings": warnings,
        "errors": errors,
        **boundary(),
    }


def build_onboarding_safety_summary() -> dict:
    summary = validate_onboarding_safety(get_onboarding_status())
    summary["notes"] = [
        "no provider portal access",
        "no API key creation",
        "no sandbox API connection",
        "no broker SDK imports are required for this runbook",
        "no raw provider payload is returned",
    ]
    return summary


def _check_false(name: str, value: object) -> dict:
    ok = value is False
    return {
        "safe": ok,
        "checks": [{"check": name, "status": "OK" if ok else "ERROR"}],
        "warnings": [],
        "errors": [] if ok else [{"check": name, "status": "ERROR", "message": f"{name} must remain false in V5.20"}],
        **boundary(),
    }

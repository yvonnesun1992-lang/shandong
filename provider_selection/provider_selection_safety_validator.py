from __future__ import annotations

import json

from config.v5_provider_selection_config import get_provider_selection_status
from provider_selection import PROVIDER_BOUNDARY


CREDENTIAL_TERMS = ["secret", "token", "password", "api_key", "authorization"]
BROKER_SDK_MARKERS = ["alpaca" + "_trade_api", "ib" + "_insync", "tiger" + "open", "robin" + "_stocks", "oauth" + "lib"]
NETWORK_MARKERS = ["requests" + ".", "httpx" + ".", "https://" + "sandbox"]
RUNTIME_MARKERS = ["account" + "_id", "real" + "_order_id", "raw provider " + "response"]


def validate_no_provider_connection() -> dict:
    status = get_provider_selection_status()
    errors = []
    if status["provider_connection_enabled"] or status["sandbox_api_enabled"] or status["broker_connected"]:
        errors.append("provider connection flag enabled")
    return {"safe": not errors, "checks": ["provider connection disabled"], "errors": errors}


def validate_no_credentials(payload: object) -> dict:
    text = json.dumps(payload, default=str).lower()
    errors = ["credential marker present"] if any(term in text for term in CREDENTIAL_TERMS) else []
    return {"safe": not errors, "errors": errors}


def validate_provider_selection_safety(payload: object | None = None) -> dict:
    status = get_provider_selection_status()
    errors = []
    checks = []
    for key in ["provider_connection_enabled", "sandbox_api_enabled", "broker_connected", "real_orders_enabled", "real_money_enabled"]:
        passed = status.get(key) is False
        checks.append({"check": key, "passed": passed})
        if not passed:
            errors.append(f"{key} must remain false")
    text = json.dumps(payload or {}, default=str).lower()
    for marker in BROKER_SDK_MARKERS + NETWORK_MARKERS + RUNTIME_MARKERS:
        if marker in text:
            errors.append("blocked provider runtime marker present")
            break
    errors.extend(validate_no_credentials(payload or {})["errors"])
    if (payload or {}).get("real_connection") is True:
        errors.append("real connection attempt blocked")
    return {"safe": not errors, "checks": checks, "warnings": status["warnings"], "errors": errors, "selection_only": True}


def build_provider_selection_safety_summary() -> dict:
    return {"version": "V5.19", **validate_provider_selection_safety(get_provider_selection_status()), **PROVIDER_BOUNDARY}

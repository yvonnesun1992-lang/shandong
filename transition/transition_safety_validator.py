from __future__ import annotations

import json

from config.v5_transition_blueprint_config import get_transition_status
from transition.credential_vault_blueprint import validate_no_credentials_present


BROKER_SDK_MARKERS = ["alpaca" + "_trade_api", "ib" + "_insync", "tiger" + "open", "robin" + "_stocks", "oauth" + "lib"]
NETWORK_MARKERS = ["requests" + ".", "httpx" + ".", "https://" + "sandbox"]
REAL_RUNTIME_MARKERS = ["account" + "_id", "real" + "_order_id", "raw provider " + "response"]


def validate_no_real_connection() -> dict:
    status = get_transition_status()
    errors = []
    if status["transition_enabled"] or status["sandbox_api_enabled"] or status["broker_connected"]:
        errors.append("real connection flag enabled")
    return {"safe": not errors, "checks": ["transition flags disabled"], "errors": errors}


def validate_no_real_order_path() -> dict:
    status = get_transition_status()
    errors = []
    if status["real_orders_enabled"] or status["real_money_enabled"]:
        errors.append("real order or real money flag enabled")
    return {"safe": not errors, "checks": ["real order path disabled"], "errors": errors}


def validate_no_credentials(payload: object) -> dict:
    credential_check = validate_no_credentials_present(payload)
    return {"safe": credential_check["valid"], "errors": [] if credential_check["valid"] else ["credential marker present"]}


def validate_transition_safety(payload: object | None = None) -> dict:
    checks = []
    errors = []
    status = get_transition_status()
    expected_false = ["transition_enabled", "sandbox_api_enabled", "broker_connected", "real_orders_enabled", "real_money_enabled"]
    for key in expected_false:
        checks.append({"check": key, "passed": status.get(key) is False})
        if status.get(key) is not False:
            errors.append(f"{key} must remain false")
    text = json.dumps(payload or {}, default=str).lower()
    for marker in BROKER_SDK_MARKERS + NETWORK_MARKERS + REAL_RUNTIME_MARKERS:
        if marker in text:
            errors.append("blocked runtime marker present")
            break
    credential = validate_no_credentials(payload or {})
    errors.extend(credential["errors"])
    return {"safe": not errors, "checks": checks, "warnings": [], "errors": errors, "blueprint_only": True}


def build_transition_safety_summary() -> dict:
    result = validate_transition_safety(get_transition_status())
    return {
        **result,
        "version": "V5.18",
        "transition_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }

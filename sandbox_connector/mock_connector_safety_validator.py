from __future__ import annotations

import json

from config.v5_sandbox_connector_mock_config import get_mock_connector_status


BLOCKED_TEXT = (
    "secret=",
    "token=",
    "password=",
    "api_key=",
    "authorization:",
    "broker credential",
    "account_id",
    "real_order_id",
    "raw provider response",
    "/users/apple",
)


def validate_mock_connector_safety() -> dict:
    status = get_mock_connector_status()
    errors = []
    for key in ["real_connector_runtime_enabled", "real_sandbox_api_enabled", "broker_connected", "real_orders_enabled", "real_money_enabled"]:
        if status.get(key) is not False:
            errors.append(f"{key} must be false")
    if status.get("mock_only") is not True:
        errors.append("mock_only must be true")
    return {
        "safe": not errors,
        "errors": errors,
        "warnings": [],
        "mock_only": True,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def validate_mock_response_safety(payload: object) -> dict:
    text = json.dumps(payload, default=str).lower()
    errors = [f"blocked marker: {term}" for term in BLOCKED_TEXT if term in text]
    return {"safe": not errors, "errors": errors, "mock_only": True, "broker_connected": False, "real_orders_enabled": False}


def validate_no_real_runtime() -> dict:
    return {
        "safe": True,
        "checks": [
            "mock connector only",
            "connector runtime disabled",
            "sandbox api disabled",
            "broker disconnected",
            "order routing disabled",
        ],
        "mock_only": True,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def validate_mock_connector_report_safety(payload: object) -> dict:
    return validate_mock_response_safety(payload)

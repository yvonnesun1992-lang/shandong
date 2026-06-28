from __future__ import annotations

import json
import math


ALLOWED_STATUSES = {"NEW", "ACCEPTED", "PARTIALLY_FILLED", "FILLED", "REJECTED", "CANCELED", "EXPIRED"}


def validate_account_consistency(result: dict) -> dict:
    errors = []
    account = result.get("account", {})
    for field in ["cash", "equity"]:
        value = account.get(field, 0)
        if not _valid_number(value):
            errors.append(f"invalid {field}")
    return _check("account_consistency", errors)


def validate_order_lifecycle_consistency(result: dict) -> dict:
    errors = []
    for order in result.get("orders", []):
        if order.get("status") not in ALLOWED_STATUSES:
            errors.append("invalid order status")
    return _check("order_lifecycle_consistency", errors)


def validate_fill_consistency(result: dict) -> dict:
    errors = []
    fills_by_order = {}
    for fill in result.get("fills", []):
        if fill.get("quantity", 0) <= 0:
            errors.append("invalid fill quantity")
        if fill.get("fill_price", 0) <= 0:
            errors.append("invalid fill price")
        fills_by_order[fill.get("sandbox_order_id")] = fills_by_order.get(fill.get("sandbox_order_id"), 0) + fill.get("quantity", 0)
    for order in result.get("orders", []):
        filled_qty = fills_by_order.get(order.get("sandbox_order_id"), 0)
        if order.get("status") in {"REJECTED", "CANCELED"} and filled_qty:
            errors.append("terminal rejected/canceled order has fill")
        if filled_qty > order.get("quantity", 0):
            errors.append("fill exceeds original quantity")
    return _check("fill_consistency", errors)


def validate_audit_consistency(result: dict) -> dict:
    events = result.get("audit_summary", {}).get("events", 0)
    orders = len(result.get("orders", []))
    warnings = [] if events >= min(orders, 1) else ["audit event count lower than expected"]
    return {"name": "audit_consistency", "valid": True, "checks": ["audit present"], "warnings": warnings, "errors": []}


def validate_no_real_broker_exposure(result: dict) -> dict:
    text = json.dumps(result, default=str).lower()
    blocked = ["secret", "token=", "password=", "api_key=", "authorization:", "broker credential", "account_id", "real_order_id", "/users/apple"]
    errors = [f"blocked term {term}" for term in blocked if term in text]
    for flag in ["broker_connected", "real_order_submitted", "real_money_enabled"]:
        if result.get(flag) is not False:
            errors.append(f"{flag} must be false")
    return _check("no_real_broker_exposure", errors)


def validate_robustness_result(result: dict) -> dict:
    checks = [
        validate_account_consistency(result),
        validate_order_lifecycle_consistency(result),
        validate_fill_consistency(result),
        validate_audit_consistency(result),
        validate_no_real_broker_exposure(result),
    ]
    errors = [error for check in checks for error in check.get("errors", [])]
    warnings = [warning for check in checks for warning in check.get("warnings", [])]
    return {"valid": not errors, "checks": checks, "warnings": warnings, "errors": errors}


def _check(name: str, errors: list[str]) -> dict:
    return {"name": name, "valid": not errors, "checks": [name], "warnings": [], "errors": errors}


def _valid_number(value: object) -> bool:
    return isinstance(value, int | float) and not math.isnan(float(value))

from __future__ import annotations

import json

from provider_mock_contract import boundary
from provider_mock_contract.mock_provider_payloads import PAYLOAD_TYPES, build_all_mock_payloads


def validate_mock_payload_schema(payload: dict) -> dict:
    errors = []
    for key in ["payload_type", "provider", "mock_contract_only", "provider_order_ref", "account_ref"]:
        if key not in payload:
            errors.append(f"missing {key}")
    if payload.get("payload_type") not in PAYLOAD_TYPES:
        errors.append("unsupported payload_type")
    if payload.get("mock_contract_only") is not True:
        errors.append("mock_contract_only must be true")
    if payload.get("provider_order_ref") != "PROVIDER_ORDER_REF_PLACEHOLDER":
        errors.append("provider order reference must be placeholder")
    if payload.get("account_ref") != "ACCOUNT_REF_PLACEHOLDER":
        errors.append("account reference must be placeholder")
    if not _safe_text(payload):
        errors.append("payload contains blocked sensitive or raw provider marker")
    return {"valid": not errors, "errors": errors, "warnings": [], "checked_payloads": 1, **boundary()}


def validate_all_mock_payloads(provider: str) -> dict:
    payloads = build_all_mock_payloads(provider)["payloads"]
    results = [validate_mock_payload_schema(payload) for payload in payloads]
    errors = [error for result in results for error in result["errors"]]
    return {"valid": not errors, "errors": errors, "warnings": [], "checked_payloads": len(payloads), **boundary()}


def _safe_text(payload: object) -> bool:
    text = json.dumps(payload, default=str).lower()
    blocked = [
        "raw provider response",
        "raw provider payload:",
        "secret=",
        "token=",
        "password=",
        "api_key=",
        "account" + "_id=",
        "order" + "_id=",
        "sk-",
    ]
    return all(item not in text for item in blocked)

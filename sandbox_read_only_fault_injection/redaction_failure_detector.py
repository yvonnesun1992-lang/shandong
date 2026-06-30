from __future__ import annotations

import json
from numbers import Number

from sandbox_read_only_fault_injection.fault_payload_catalog import FAULT_TYPES, build_fault_payload
from sandbox_read_only_fault_injection.init import boundary

VALUE_KEYS = ["cash_balance", "buying_power", "market_value", "quantity", "unrealized_pnl", "average_cost"]
TERM_KEYS = [
    "account_id",
    "raw_provider_payload",
    "provider_endpoint_url",
    "api_key",
    "secret",
    "token",
    "password",
    "authorization",
]


def detect_redaction_failure(payload: dict | list | str) -> dict:
    findings: list[str] = []
    if isinstance(payload, dict):
        if payload.get("account_ref") not in {None, "ACCOUNT_REF_PLACEHOLDER"}:
            findings.append("non-placeholder account_ref")
        for key in TERM_KEYS:
            if key in payload:
                findings.append(f"{key} exposure")
        for key in VALUE_KEYS:
            if isinstance(payload.get(key), Number):
                findings.append(f"numeric {key}")
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    for term in ["mock_raw_provider_payload", "mock_provider_endpoint_url", "mock_api_key", "mock_token"]:
        if term in text:
            findings.append(f"{term} detected")
    return {
        **boundary(),
        "redaction_failure_detected": bool(findings),
        "findings": findings,
        "warnings": findings,
    }


def detect_all_redaction_failures(provider: str = "alpaca") -> dict:
    results = [detect_redaction_failure(build_fault_payload(provider, fault_type)) for fault_type in FAULT_TYPES]
    return {
        **boundary(),
        "provider": provider,
        "redaction_failures_detected": any(result["redaction_failure_detected"] for result in results),
        "results": results,
        "findings": [finding for result in results for finding in result["findings"]],
    }

from __future__ import annotations

import json
from numbers import Number

from sandbox_read_only_mock_replay.init import boundary
from sandbox_read_only_mock_replay.mock_read_only_payloads import PAYLOAD_TYPES, REDACTED_PLACEHOLDER, build_mock_read_only_payload

UNREDACTED_VALUE_KEYS = ["cash_balance", "buying_power", "market_value", "unrealized_pnl", "quantity"]
BLOCKED_TERMS = [
    "api_key=demo",
    "secret_value=demo",
    "token=demo",
    "password=demo",
    "authorization",
    "real_order_id",
    "account_id",
    "raw provider response",
    "raw provider payload",
    "provider_endpoint_url",
    "paper-api.",
    "api.alpaca.",
]


def validate_payload_redaction(payload: dict | list | str) -> dict:
    findings: list[str] = []
    if isinstance(payload, dict):
        for key in UNREDACTED_VALUE_KEYS:
            if key in payload and payload.get(key) != REDACTED_PLACEHOLDER:
                findings.append(f"{key} must be redacted")
            if isinstance(payload.get(key), Number):
                findings.append(f"{key} must not be numeric")
        if payload.get("raw_payload_stored") is True:
            findings.append("raw payload storage must remain disabled")
        if payload.get("provider_payload_redacted") is False:
            findings.append("provider payload must remain redacted")
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    for term in BLOCKED_TERMS:
        if term in text:
            findings.append(f"blocked term detected: {term}")
    return {
        **boundary(),
        "redaction_valid": not findings,
        "findings": findings,
        "warnings": [] if not findings else ["redaction validation failed"],
    }


def validate_all_payload_redaction(provider: str = "alpaca") -> dict:
    results = [validate_payload_redaction(build_mock_read_only_payload(provider, payload_type)) for payload_type in PAYLOAD_TYPES]
    redaction_valid = all(result["redaction_valid"] for result in results)
    return {
        **boundary(),
        "provider": provider,
        "redaction_valid": redaction_valid,
        "results": results,
        "warnings": [] if redaction_valid else ["read-only mock redaction failed"],
    }

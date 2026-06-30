from __future__ import annotations

import json

from sandbox_read_only_connector.init import boundary


BLOCKED_TRUE_FIELDS = [
    "read_only_runtime_enabled",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "position_read_enabled",
    "balance_read_enabled",
    "order_preview_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]

BLOCKED_TERMS = [
    "alpaca_trade_api",
    "ib_insync",
    "tigeropen",
    "robin_stocks",
    "oauthlib",
    "https://sandbox",
    "paper-api.",
    "provider_endpoint_url",
    "api_key=",
    "secret_value=",
    "token=",
    "password=",
    "authorization:",
    "account_id",
    "real_order_id",
    "raw provider response",
    "raw provider payload",
]

UNREDACTED_VALUE_KEYS = [
    "cash_balance",
    "buying_power",
    "market_value",
    "unrealized_pnl",
    "quantity",
]


def validate_read_only_safety(payload: dict | list | str | None = None) -> dict:
    payload = payload or {}
    findings: list[str] = []
    if isinstance(payload, dict):
        for field in BLOCKED_TRUE_FIELDS:
            if payload.get(field) is True:
                findings.append(f"{field} must remain false in V5.33")
        for key in UNREDACTED_VALUE_KEYS:
            if key in payload and f"{key}_placeholder" not in payload:
                findings.append(f"{key} must be redacted in V5.33")
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    for term in BLOCKED_TERMS:
        if term in text:
            findings.append(f"blocked term detected: {term}")
    return {
        **boundary(),
        "safe": not findings,
        "findings": findings,
        "warnings": [] if not findings else ["read-only connector safety boundary violation detected"],
    }


def build_read_only_safety_summary() -> dict:
    return {
        **boundary(),
        "safe": True,
        "checks": [
            "read-only runtime disabled",
            "sandbox API disabled",
            "credential read disabled",
            "account read disabled",
            "position read disabled",
            "balance read disabled",
            "order preview disabled",
            "order submission disabled",
            "broker disconnected",
            "real money disabled",
            "no broker SDK imports",
            "no network calls",
            "no plaintext credentials",
            "no account or order identifiers",
            "no raw provider payload",
            "no unredacted balance or position values",
        ],
        "warnings": ["read-only connector remains blueprint-only in V5.33"],
    }

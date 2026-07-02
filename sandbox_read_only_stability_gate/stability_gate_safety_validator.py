from __future__ import annotations

import json
from numbers import Number

from sandbox_read_only_stability_gate.init import boundary

BLOCKED_TRUE_FIELDS = [
    "stability_gate_runtime_enabled",
    "stability_gate_passed",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "position_read_enabled",
    "balance_read_enabled",
    "order_preview_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
    "read_only_connector_allowed",
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
    "api_key=demo",
    "secret_value=demo",
    "mock_api_key",
    "mock_token",
    "token=demo",
    "password=demo",
    "authorization",
    "real_account_id",
    "real_order_id",
    "raw real provider payload",
]

UNREDACTED_VALUE_KEYS = ["cash_balance", "buying_power", "market_value", "unrealized_pnl", "quantity", "average_cost"]


def validate_stability_gate_safety(payload: dict | list | str | None = None) -> dict:
    payload = payload or {}
    findings: list[str] = []
    if isinstance(payload, dict):
        for field in BLOCKED_TRUE_FIELDS:
            if payload.get(field) is True:
                findings.append(f"{field} must remain false in V5.36")
        for key in UNREDACTED_VALUE_KEYS:
            if isinstance(payload.get(key), Number):
                findings.append(f"{key} must not contain numeric values in V5.36")
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    for term in BLOCKED_TERMS:
        if term in text:
            findings.append(f"blocked term detected: {term}")
    return {
        **boundary(),
        "safe": not findings,
        "findings": findings,
        "warnings": [] if not findings else ["read-only stability gate safety boundary violation detected"],
    }


def build_stability_gate_safety_summary() -> dict:
    return {
        **boundary(),
        "safe": True,
        "checks": [
            "stability gate runtime disabled",
            "stability gate pass disabled",
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
            "no real plaintext credentials",
            "no real account or order identifiers",
            "no real provider raw payload",
            "no real provider endpoint URL",
            "no unredacted real balances or positions",
        ],
        "warnings": ["read-only stability gate remains blocked in V5.36"],
    }

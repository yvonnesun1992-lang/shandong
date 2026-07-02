from __future__ import annotations

import json
from numbers import Number

from sandbox_read_only_final_review.init import boundary

BLOCKED_TRUE_FIELDS = [
    "final_review_runtime_enabled",
    "final_review_passed",
    "read_only_connector_allowed",
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


def validate_final_review_safety(payload: dict | list | str | None = None) -> dict:
    payload = payload or {}
    findings: list[str] = []
    if isinstance(payload, dict):
        for field in BLOCKED_TRUE_FIELDS:
            if payload.get(field) is True:
                findings.append(f"{field} must remain false in V5.38")
        for key in UNREDACTED_VALUE_KEYS:
            if isinstance(payload.get(key), Number):
                findings.append(f"{key} must not contain numeric values in V5.38")
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    for term in BLOCKED_TERMS:
        if term in text:
            findings.append(f"blocked term detected: {term}")
    return {
        **boundary(),
        "safe": not findings,
        "findings": findings,
        "warnings": [] if not findings else ["read-only final review safety boundary violation detected"],
    }


def build_final_review_safety_summary() -> dict:
    return {
        **boundary(),
        "safe": True,
        "checks": [
            "final review runtime disabled",
            "final review pass disabled",
            "read-only connector disabled",
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
            "no real account or order identifiers",
            "no raw provider payload",
            "no real provider endpoint URL",
            "no unredacted real balances or positions",
        ],
        "warnings": ["read-only final review remains review-only in V5.38"],
    }


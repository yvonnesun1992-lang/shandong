from __future__ import annotations

import json
from numbers import Number

from sandbox_read_only_mock_replay.init import boundary

BLOCKED_TRUE_FIELDS = [
    "mock_replay_runtime_enabled",
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
    "authorization",
    "account_id",
    "real_order_id",
    "raw provider response",
    "raw provider payload",
]

UNREDACTED_VALUE_KEYS = ["cash_balance", "buying_power", "market_value", "unrealized_pnl", "quantity"]


def validate_read_only_mock_replay_safety(payload: dict | list | str | None = None) -> dict:
    payload = payload or {}
    findings: list[str] = []
    if isinstance(payload, dict):
        for field in BLOCKED_TRUE_FIELDS:
            if payload.get(field) is True:
                findings.append(f"{field} must remain false in V5.34")
        for key in UNREDACTED_VALUE_KEYS:
            if key in payload and isinstance(payload.get(key), Number):
                findings.append(f"{key} must not contain numeric values in V5.34")
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    for term in BLOCKED_TERMS:
        if term in text:
            findings.append(f"blocked term detected: {term}")
    return {
        **boundary(),
        "safe": not findings,
        "findings": findings,
        "warnings": [] if not findings else ["read-only mock replay safety boundary violation detected"],
    }


def build_read_only_mock_replay_safety_summary() -> dict:
    return {
        **boundary(),
        "safe": True,
        "checks": [
            "mock replay runtime disabled",
            "sandbox API disabled",
            "credential read disabled",
            "account read disabled",
            "position read disabled",
            "balance read disabled",
            "order preview disabled",
            "order submission disabled",
            "broker disconnected",
            "real money disabled",
            "payload values redacted",
            "provider payload storage disabled",
            "local replay only",
        ],
        "warnings": ["read-only mock replay remains local-only in V5.34"],
    }

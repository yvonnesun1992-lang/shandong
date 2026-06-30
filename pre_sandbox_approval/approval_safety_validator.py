from __future__ import annotations

import json

from pre_sandbox_approval.init import boundary


BLOCKED_TRUE_FIELDS = [
    "approval_runtime_enabled",
    "operator_approval_granted",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "broker_connected",
    "order_submission_enabled",
    "real_money_enabled",
]

BLOCKED_TERMS = [
    "alpaca_trade_api",
    "ib_insync",
    "tigeropen",
    "robin_stocks",
    "https://sandbox",
    "paper-api.",
    "provider_endpoint_url",
    "provider portal login",
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


def validate_approval_safety(payload: dict | list | str | None = None) -> dict:
    payload = payload or {}
    findings: list[str] = []
    if isinstance(payload, dict):
        for field in BLOCKED_TRUE_FIELDS:
            if payload.get(field) is True:
                findings.append(f"{field} must remain false in V5.28")
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    for term in BLOCKED_TERMS:
        if term in text:
            findings.append(f"blocked term detected: {term}")
    return {
        **boundary(),
        "safe": not findings,
        "findings": findings,
        "warnings": [] if not findings else ["approval safety boundary violation detected"],
    }


def build_approval_safety_summary() -> dict:
    return {
        **boundary(),
        "safe": True,
        "checks": [
            "approval runtime disabled",
            "operator approval cannot unlock sandbox",
            "sandbox API disabled",
            "secret read disabled",
            "broker disconnected",
            "order submission disabled",
            "real money disabled",
            "no broker SDK imports",
            "no network calls",
            "no plaintext credentials",
            "no raw provider payload",
        ],
        "warnings": ["approval gate remains blocked in V5.28"],
    }

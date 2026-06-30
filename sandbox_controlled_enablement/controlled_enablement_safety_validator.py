from __future__ import annotations

import json

from sandbox_controlled_enablement.init import boundary


BLOCKED_TRUE_FIELDS = [
    "controlled_enablement_runtime_enabled",
    "controlled_go_enabled",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
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


def validate_controlled_enablement_safety(payload: dict | list | str | None = None) -> dict:
    payload = payload or {}
    findings: list[str] = []
    if isinstance(payload, dict):
        for field in BLOCKED_TRUE_FIELDS:
            if payload.get(field) is True:
                findings.append(f"{field} must remain false in V5.32")
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    for term in BLOCKED_TERMS:
        if term in text:
            findings.append(f"blocked term detected: {term}")
    return {
        **boundary(),
        "safe": not findings,
        "findings": findings,
        "warnings": [] if not findings else ["controlled enablement safety boundary violation detected"],
    }


def build_controlled_enablement_safety_summary() -> dict:
    return {
        **boundary(),
        "safe": True,
        "checks": [
            "controlled runtime disabled",
            "controlled GO disabled",
            "sandbox API disabled",
            "secret read disabled",
            "account read disabled",
            "order preview disabled",
            "order submission disabled",
            "broker disconnected",
            "real money disabled",
            "no broker SDK imports",
            "no network calls",
            "no plaintext credentials",
            "no account or order identifiers",
            "no raw provider payload",
        ],
        "warnings": ["controlled GO remains blocked in V5.32"],
    }

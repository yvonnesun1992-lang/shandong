from __future__ import annotations

import json

from sandbox_read_only_connector.init import boundary


POLICY_ITEMS = [
    "account refs redacted",
    "balances redacted by default",
    "positions quantities redacted by default",
    "provider payload redacted",
    "raw payload never stored",
    "logs contain placeholders only",
    "frontend receives redacted values only",
    "audit references placeholder refs only",
]

UNREDACTED_TERMS = [
    "cash_balance",
    "buying_power",
    "market_value",
    "unrealized_pnl",
    "quantity",
    "average_cost",
    "account_id",
    "raw provider payload",
    "raw provider response",
]


def build_redaction_policy(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "redaction_policy": POLICY_ITEMS.copy(),
        "redaction_ready": False,
        "frontend_redacted_only": True,
        "raw_payload_stored": False,
    }


def validate_redacted_payload(payload: dict | list | str | None = None) -> dict:
    payload = payload or {}
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = [term for term in UNREDACTED_TERMS if term in text and f"{term}_placeholder" not in text]
    return {
        **boundary(),
        "redacted": not findings,
        "findings": findings,
        "warnings": [] if not findings else ["unredacted read-only payload value detected"],
    }

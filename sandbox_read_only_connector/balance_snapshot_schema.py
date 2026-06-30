from __future__ import annotations

from sandbox_read_only_connector.init import boundary


def build_balance_snapshot_schema(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "schema": {
            "account_ref_placeholder": "ACCOUNT_REF_REDACTED",
            "cash_balance_placeholder": "VALUE_REDACTED",
            "buying_power_placeholder": "VALUE_REDACTED",
            "margin_available_placeholder": "VALUE_REDACTED",
            "currency_placeholder": "CURRENCY_PLACEHOLDER",
            "timestamp_placeholder": "TIMESTAMP_PLACEHOLDER",
            "value_redacted": True,
            "raw_payload_stored": False,
        },
    }

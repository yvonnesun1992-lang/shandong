from __future__ import annotations

from sandbox_read_only_connector.init import boundary


def build_position_snapshot_schema(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "schema": {
            "account_ref_placeholder": "ACCOUNT_REF_REDACTED",
            "symbol_placeholder": "SYMBOL_PLACEHOLDER",
            "quantity_placeholder": "VALUE_REDACTED",
            "average_cost_placeholder": "VALUE_REDACTED",
            "market_value_placeholder": "VALUE_REDACTED",
            "unrealized_pnl_placeholder": "VALUE_REDACTED",
            "currency_placeholder": "CURRENCY_PLACEHOLDER",
            "timestamp_placeholder": "TIMESTAMP_PLACEHOLDER",
            "value_redacted": True,
            "raw_payload_stored": False,
        },
    }

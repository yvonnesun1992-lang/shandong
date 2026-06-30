from __future__ import annotations

from sandbox_read_only_connector.init import boundary


def build_account_snapshot_schema(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "schema": {
            "account_ref_placeholder": "ACCOUNT_REF_REDACTED",
            "provider": provider,
            "account_status_placeholder": "STATUS_PLACEHOLDER",
            "account_type_placeholder": "TYPE_PLACEHOLDER",
            "currency_placeholder": "CURRENCY_PLACEHOLDER",
            "timestamp_placeholder": "TIMESTAMP_PLACEHOLDER",
            "raw_payload_stored": False,
            "provider_payload_redacted": True,
        },
    }

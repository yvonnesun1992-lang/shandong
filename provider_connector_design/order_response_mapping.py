from __future__ import annotations

from provider_connector_design import boundary


NORMALIZED_FIELDS = [
    "provider_order_ref_placeholder",
    "internal_order_id",
    "client_order_id",
    "order_status",
    "filled_quantity",
    "remaining_quantity",
    "average_fill_price",
    "submitted_at",
    "updated_at",
    "rejection_reason",
    "raw_response_redacted",
]


def build_order_response_mapping(provider: str) -> dict:
    return {
        "provider": provider,
        "response_mapping": {field: "placeholder_redacted_only" if field == "raw_response_redacted" else f"{field}_placeholder" for field in NORMALIZED_FIELDS},
        "normalization_rules": [
            "raw provider payload is never stored",
            "provider references remain placeholders in V5.21",
            "unknown states require manual review in future connector work",
        ],
        "raw_response_policy": "redacted_only",
        **boundary(),
    }

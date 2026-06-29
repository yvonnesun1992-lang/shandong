from __future__ import annotations

from provider_connector_design import boundary


REQUIRED_INTERNAL_FIELDS = [
    "internal_order_id",
    "client_order_id",
    "symbol",
    "side",
    "order_type",
    "quantity",
    "limit_price",
    "stop_price",
    "time_in_force",
    "notional",
    "strategy_id",
    "approval_id",
    "risk_check_id",
    "idempotency_key",
]


def build_order_request_mapping(provider: str) -> dict:
    return {
        "provider": provider,
        "request_mapping": {field: f"{field}_provider_placeholder" for field in REQUIRED_INTERNAL_FIELDS},
        "required_internal_fields": REQUIRED_INTERNAL_FIELDS.copy(),
        "provider_fields_placeholder": ["provider_request_schema_placeholder", "provider_order_endpoint_placeholder_disabled"],
        "validation_rules": [
            "manual approval id is required before future submission",
            "risk check id is required before future submission",
            "idempotency key is required before future submission",
            "provider request construction remains disabled in V5.21",
        ],
        **boundary(),
    }

from __future__ import annotations

from provider_mock_contract import boundary


PAYLOAD_TYPES = [
    "accepted_order_response",
    "partial_fill_response",
    "filled_order_response",
    "rejected_order_response",
    "canceled_order_response",
    "account_snapshot_placeholder",
    "position_snapshot_placeholder",
    "rate_limit_error",
    "invalid_symbol_error",
    "insufficient_funds_error",
    "market_closed_error",
    "provider_timeout_error",
    "duplicate_order_error",
]

STATUS_BY_TYPE = {
    "accepted_order_response": "accepted",
    "partial_fill_response": "partial_fill",
    "filled_order_response": "filled",
    "rejected_order_response": "rejected",
    "canceled_order_response": "canceled",
}

ERROR_BY_TYPE = {
    "rate_limit_error": "RATE_LIMITED",
    "invalid_symbol_error": "INVALID_SYMBOL",
    "insufficient_funds_error": "INSUFFICIENT_FUNDS",
    "market_closed_error": "MARKET_CLOSED",
    "provider_timeout_error": "PROVIDER_TIMEOUT",
    "duplicate_order_error": "DUPLICATE_ORDER",
}


def build_mock_payload(provider: str, payload_type: str) -> dict:
    if payload_type not in PAYLOAD_TYPES:
        payload_type = "accepted_order_response"
    payload = {
        "provider": provider,
        "payload_type": payload_type,
        "provider_order_ref": "PROVIDER_ORDER_REF_PLACEHOLDER",
        "account_ref": "ACCOUNT_REF_PLACEHOLDER",
        "client_order_id": "CLIENT_ORDER_ID_PLACEHOLDER",
        "internal_order_id": "INTERNAL_ORDER_ID_PLACEHOLDER",
        "raw_payload_stored": False,
        "provider_endpoint_url": "DISABLED_PROVIDER_ENDPOINT_PLACEHOLDER",
        **boundary(),
    }
    if payload_type in STATUS_BY_TYPE:
        payload.update(
            {
                "status": STATUS_BY_TYPE[payload_type],
                "filled_quantity": 10 if payload_type == "filled_order_response" else 5 if payload_type == "partial_fill_response" else 0,
                "remaining_quantity": 0 if payload_type == "filled_order_response" else 5,
                "average_fill_price": "AVERAGE_FILL_PRICE_PLACEHOLDER",
                "rejection_reason": "REJECTION_REASON_PLACEHOLDER" if payload_type == "rejected_order_response" else "",
            }
        )
    elif payload_type in ERROR_BY_TYPE:
        payload.update({"internal_error_type": ERROR_BY_TYPE[payload_type], "provider_error_code": "PROVIDER_ERROR_CODE_PLACEHOLDER"})
    elif payload_type == "account_snapshot_placeholder":
        payload.update({"account_status": "ACCOUNT_STATUS_PLACEHOLDER", "cash_balance": "CASH_BALANCE_PLACEHOLDER", "buying_power": "BUYING_POWER_PLACEHOLDER"})
    elif payload_type == "position_snapshot_placeholder":
        payload.update({"position_symbol": "SYMBOL_PLACEHOLDER", "position_quantity": "QUANTITY_PLACEHOLDER", "market_value": "MARKET_VALUE_PLACEHOLDER"})
    return payload


def build_all_mock_payloads(provider: str) -> dict:
    return {"provider": provider, "payloads": [build_mock_payload(provider, payload_type) for payload_type in PAYLOAD_TYPES], **boundary()}

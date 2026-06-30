from __future__ import annotations

from config.v5_read_only_fault_injection_config import get_read_only_fault_injection_provider
from sandbox_read_only_fault_injection.init import boundary

FAULT_TYPES = [
    "unredacted_account_id",
    "unredacted_cash_balance",
    "unredacted_buying_power",
    "unredacted_position_quantity",
    "unredacted_market_value",
    "unredacted_unrealized_pnl",
    "raw_provider_payload_present",
    "provider_endpoint_url_present",
    "api_key_present",
    "token_present",
    "stale_snapshot",
    "malformed_account_snapshot",
    "malformed_balance_snapshot",
    "malformed_position_snapshot",
    "audit_write_failure",
    "rate_limit_error",
    "unknown_provider_payload",
    "unexpected_order_preview_flag",
    "unexpected_order_submission_flag",
]


def build_fault_payload(provider: str | None = None, fault_type: str = "unredacted_account_id") -> dict:
    selected = provider or get_read_only_fault_injection_provider()
    selected_fault = fault_type if fault_type in FAULT_TYPES else "unknown_provider_payload"
    payload = {
        **boundary(),
        "provider": selected,
        "fault_type": selected_fault,
        "payload_type": "fault_snapshot_placeholder",
        "account_ref": "ACCOUNT_REF_PLACEHOLDER",
        "timestamp_placeholder": "TIMESTAMP_PLACEHOLDER",
        "raw_payload_stored": False,
        "provider_payload_redacted": True,
        "values_redacted": True,
        "network_call_made": False,
        "order_submitted": False,
        "expected_detection": "blocked",
    }
    if selected_fault == "unredacted_account_id":
        payload["account_id"] = "FAKE_ACCOUNT_ID_FOR_TEST_ONLY"
        payload["account_ref"] = "FAKE_ACCOUNT_REF_FOR_TEST_ONLY"
    elif selected_fault == "unredacted_cash_balance":
        payload["cash_balance"] = 12345.67
    elif selected_fault == "unredacted_buying_power":
        payload["buying_power"] = 23456.78
    elif selected_fault == "unredacted_position_quantity":
        payload["quantity"] = 100
    elif selected_fault == "unredacted_market_value":
        payload["market_value"] = 9999.99
    elif selected_fault == "unredacted_unrealized_pnl":
        payload["unrealized_pnl"] = 321.0
    elif selected_fault == "raw_provider_payload_present":
        payload["raw_provider_payload"] = "MOCK_RAW_PROVIDER_PAYLOAD_FOR_TEST_ONLY"
        payload["raw_payload_stored"] = True
    elif selected_fault == "provider_endpoint_url_present":
        payload["provider_endpoint_url"] = "MOCK_PROVIDER_ENDPOINT_URL_FOR_TEST_ONLY"
    elif selected_fault == "api_key_present":
        payload["api_key"] = "MOCK_API_KEY_FOR_TEST_ONLY"
    elif selected_fault == "token_present":
        payload["token"] = "MOCK_TOKEN_FOR_TEST_ONLY"
    elif selected_fault == "stale_snapshot":
        payload.update(
            {
                "stale_snapshot": True,
                "snapshot_age_seconds": 999999,
                "timestamp_placeholder_expired": True,
                "market_session_mismatch_placeholder": True,
            }
        )
    elif selected_fault == "malformed_account_snapshot":
        payload.pop("account_ref", None)
        payload["payload_type"] = "account_snapshot_malformed"
    elif selected_fault == "malformed_balance_snapshot":
        payload.pop("timestamp_placeholder", None)
        payload["payload_type"] = "balance_snapshot_malformed"
        payload["values_redacted"] = False
    elif selected_fault == "malformed_position_snapshot":
        payload["payload_type"] = "position_snapshot_malformed"
        payload["provider_payload_redacted"] = False
    elif selected_fault == "audit_write_failure":
        payload["audit_write_success"] = False
    elif selected_fault == "rate_limit_error":
        payload["rate_limit_error"] = True
    elif selected_fault == "unknown_provider_payload":
        payload["payload_type"] = "unknown_provider_payload"
    elif selected_fault == "unexpected_order_preview_flag":
        payload["order_preview_enabled"] = True
        payload["trade_intent"] = "MOCK_TRADE_INTENT_FOR_TEST_ONLY"
    elif selected_fault == "unexpected_order_submission_flag":
        payload["order_submission_enabled"] = True
        payload["order_submitted"] = True
        payload["sandbox_order_id"] = "MOCK_SANDBOX_ORDER_ID_FOR_TEST_ONLY"
        payload["submit_order"] = "MOCK_SUBMIT_ORDER_FOR_TEST_ONLY"
    return payload


def build_all_fault_payloads(provider: str | None = None) -> dict:
    selected = provider or get_read_only_fault_injection_provider()
    return {
        **boundary(),
        "provider": selected,
        "fault_payloads": [build_fault_payload(selected, fault_type) for fault_type in FAULT_TYPES],
        "fault_count": len(FAULT_TYPES),
    }

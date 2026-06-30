from __future__ import annotations

from config.v5_read_only_mock_replay_config import get_read_only_mock_replay_provider
from sandbox_read_only_mock_replay.init import boundary

PAYLOAD_TYPES = [
    "account_snapshot_placeholder",
    "balance_snapshot_placeholder",
    "position_snapshot_placeholder",
    "error_snapshot_placeholder",
]

REDACTED_PLACEHOLDER = "REDACTED_PLACEHOLDER"
ACCOUNT_REF_PLACEHOLDER = "ACCOUNT_REF_PLACEHOLDER"


def build_mock_read_only_payload(provider: str | None = None, payload_type: str = "account_snapshot_placeholder") -> dict:
    selected = provider or get_read_only_mock_replay_provider()
    if payload_type not in PAYLOAD_TYPES:
        payload_type = "error_snapshot_placeholder"
    payload = {
        **boundary(),
        "provider": selected,
        "payload_type": payload_type,
        "mock_payload_id": f"{selected}:{payload_type}",
        "timestamp_placeholder": "TIMESTAMP_PLACEHOLDER",
        "raw_payload_stored": False,
        "provider_payload_redacted": True,
        "values_redacted": True,
        "network_call_made": False,
    }
    if payload_type == "account_snapshot_placeholder":
        payload.update(
            {
                "account_ref": ACCOUNT_REF_PLACEHOLDER,
                "account_status": "PLACEHOLDER_ONLY",
                "permissions": ["READ_ONLY_PLACEHOLDER"],
            }
        )
    elif payload_type == "balance_snapshot_placeholder":
        payload.update(
            {
                "account_ref": ACCOUNT_REF_PLACEHOLDER,
                "cash_balance": REDACTED_PLACEHOLDER,
                "buying_power": REDACTED_PLACEHOLDER,
                "currency": "REDACTED_CURRENCY_PLACEHOLDER",
            }
        )
    elif payload_type == "position_snapshot_placeholder":
        payload.update(
            {
                "account_ref": ACCOUNT_REF_PLACEHOLDER,
                "symbol": "SYMBOL_PLACEHOLDER",
                "quantity": REDACTED_PLACEHOLDER,
                "market_value": REDACTED_PLACEHOLDER,
                "unrealized_pnl": REDACTED_PLACEHOLDER,
            }
        )
    else:
        payload.update(
            {
                "error_code": "MOCK_REPLAY_PLACEHOLDER",
                "error_message": "REDACTED_ERROR_PLACEHOLDER",
                "recoverable": True,
            }
        )
    return payload


def build_all_mock_read_only_payloads(provider: str | None = None) -> dict:
    selected = provider or get_read_only_mock_replay_provider()
    return {
        **boundary(),
        "provider": selected,
        "payloads": [build_mock_read_only_payload(selected, payload_type) for payload_type in PAYLOAD_TYPES],
        "payload_count": len(PAYLOAD_TYPES),
        "raw_payload_stored": False,
        "provider_payload_redacted": True,
        "values_redacted": True,
    }

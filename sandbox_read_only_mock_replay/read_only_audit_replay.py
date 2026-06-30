from __future__ import annotations

from sandbox_read_only_mock_replay.init import boundary
from sandbox_read_only_mock_replay.mock_read_only_payloads import PAYLOAD_TYPES


def build_read_only_mock_audit_event(provider: str = "alpaca", payload_type: str = "account_snapshot_placeholder") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "payload_type": payload_type,
        "read_only_mock_audit_id_placeholder": "READ_ONLY_MOCK_AUDIT_PLACEHOLDER",
        "actor": "read_only_mock_replay",
        "account_read": False,
        "balance_read": False,
        "position_read": False,
        "order_previewed": False,
        "order_submitted": False,
        "raw_payload_stored": False,
        "provider_payload_redacted": True,
        "values_redacted": True,
    }


def build_read_only_mock_audit_trail(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "audit_events": [build_read_only_mock_audit_event(provider, payload_type) for payload_type in PAYLOAD_TYPES],
        "audit_written": True,
    }

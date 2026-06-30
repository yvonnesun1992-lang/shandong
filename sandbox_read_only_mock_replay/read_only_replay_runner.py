from __future__ import annotations

from sandbox_read_only_mock_replay.init import boundary
from sandbox_read_only_mock_replay.mock_read_only_payloads import PAYLOAD_TYPES, build_mock_read_only_payload
from sandbox_read_only_mock_replay.read_only_audit_replay import build_read_only_mock_audit_event, build_read_only_mock_audit_trail
from sandbox_read_only_mock_replay.read_only_schema_validator import validate_payload_schema
from sandbox_read_only_mock_replay.redaction_replay_validator import validate_payload_redaction


def run_read_only_replay_payload(provider: str = "alpaca", payload_type: str = "account_snapshot_placeholder") -> dict:
    payload = build_mock_read_only_payload(provider, payload_type)
    schema = validate_payload_schema(payload)
    redaction = validate_payload_redaction(payload)
    audit = build_read_only_mock_audit_event(provider, payload_type)
    accepted = schema["schema_valid"] and redaction["redaction_valid"]
    return {
        **boundary(),
        "provider": provider,
        "payload_type": payload_type,
        "accepted": accepted,
        "schema_valid": schema["schema_valid"],
        "redaction_valid": redaction["redaction_valid"],
        "audit_written": True,
        "payload": payload,
        "audit": audit,
        "warnings": schema.get("warnings", []) + redaction.get("warnings", []),
    }


def run_read_only_replay(provider: str = "alpaca") -> dict:
    results = [run_read_only_replay_payload(provider, payload_type) for payload_type in PAYLOAD_TYPES]
    accepted_count = sum(1 for result in results if result["accepted"])
    return {
        **boundary(),
        "provider": provider,
        "results": results,
        "accepted_count": accepted_count,
        "rejected_count": len(results) - accepted_count,
        "audit_trail": build_read_only_mock_audit_trail(provider),
        "warnings": [warning for result in results for warning in result.get("warnings", [])],
    }

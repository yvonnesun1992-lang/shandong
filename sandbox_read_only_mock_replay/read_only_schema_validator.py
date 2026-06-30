from __future__ import annotations

from sandbox_read_only_mock_replay.init import boundary
from sandbox_read_only_mock_replay.mock_read_only_payloads import (
    ACCOUNT_REF_PLACEHOLDER,
    PAYLOAD_TYPES,
    REDACTED_PLACEHOLDER,
    build_mock_read_only_payload,
)


def validate_account_schema(payload: dict) -> dict:
    return _schema_result(payload, payload.get("account_ref") == ACCOUNT_REF_PLACEHOLDER)


def validate_balance_schema(payload: dict) -> dict:
    valid = (
        payload.get("cash_balance") == REDACTED_PLACEHOLDER
        and payload.get("buying_power") == REDACTED_PLACEHOLDER
        and payload.get("account_ref") == ACCOUNT_REF_PLACEHOLDER
    )
    return _schema_result(payload, valid)


def validate_position_schema(payload: dict) -> dict:
    valid = (
        payload.get("quantity") == REDACTED_PLACEHOLDER
        and payload.get("market_value") == REDACTED_PLACEHOLDER
        and payload.get("account_ref") == ACCOUNT_REF_PLACEHOLDER
    )
    return _schema_result(payload, valid)


def validate_payload_schema(payload: dict) -> dict:
    payload_type = payload.get("payload_type")
    if payload_type == "account_snapshot_placeholder":
        return validate_account_schema(payload)
    if payload_type == "balance_snapshot_placeholder":
        return validate_balance_schema(payload)
    if payload_type == "position_snapshot_placeholder":
        return validate_position_schema(payload)
    return _schema_result(payload, payload_type == "error_snapshot_placeholder")


def validate_all_read_only_schemas(provider: str = "alpaca") -> dict:
    results = [validate_payload_schema(build_mock_read_only_payload(provider, payload_type)) for payload_type in PAYLOAD_TYPES]
    schema_valid = all(result["schema_valid"] for result in results)
    return {
        **boundary(),
        "provider": provider,
        "schema_valid": schema_valid,
        "results": results,
        "warnings": [] if schema_valid else ["read-only mock payload schema failed"],
    }


def _schema_result(payload: dict, valid: bool) -> dict:
    base_valid = (
        payload.get("raw_payload_stored") is False
        and payload.get("provider_payload_redacted") is True
        and payload.get("values_redacted") is True
        and payload.get("read_only_mock_replay_only") is True
    )
    return {
        **boundary(),
        "provider": payload.get("provider", "alpaca"),
        "payload_type": payload.get("payload_type", "unknown"),
        "schema_valid": bool(valid and base_valid),
        "raw_payload_stored": False,
        "provider_payload_redacted": True,
        "values_redacted": True,
    }

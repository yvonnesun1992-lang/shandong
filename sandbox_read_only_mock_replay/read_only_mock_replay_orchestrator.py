from __future__ import annotations

from sandbox_read_only_mock_replay.init import boundary
from sandbox_read_only_mock_replay.mock_read_only_payloads import build_all_mock_read_only_payloads
from sandbox_read_only_mock_replay.read_only_audit_replay import build_read_only_mock_audit_trail
from sandbox_read_only_mock_replay.read_only_mock_replay_safety_validator import build_read_only_mock_replay_safety_summary, validate_read_only_mock_replay_safety
from sandbox_read_only_mock_replay.read_only_replay_runner import run_read_only_replay
from sandbox_read_only_mock_replay.read_only_schema_validator import validate_all_read_only_schemas
from sandbox_read_only_mock_replay.redaction_replay_validator import validate_all_payload_redaction


def run_read_only_mock_replay(provider: str = "alpaca") -> dict:
    result = {
        **boundary(),
        "provider": provider,
        "payloads": build_all_mock_read_only_payloads(provider),
        "schema": validate_all_read_only_schemas(provider),
        "redaction": validate_all_payload_redaction(provider),
        "replay": run_read_only_replay(provider),
        "audit": build_read_only_mock_audit_trail(provider),
        "safety": build_read_only_mock_replay_safety_summary(),
    }
    result["self_validation"] = validate_read_only_mock_replay_safety(result)
    return result


def summarize_read_only_mock_replay(result: dict) -> dict:
    warnings = []
    for key in ["schema", "redaction", "replay", "audit", "safety", "self_validation"]:
        warnings.extend(result.get(key, {}).get("warnings", []))
    safe = (
        result.get("schema", {}).get("schema_valid", False)
        and result.get("redaction", {}).get("redaction_valid", False)
        and result.get("safety", {}).get("safe", False)
        and result.get("self_validation", {}).get("safe", False)
    )
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "verdict": "WARNING" if warnings and safe else "PASS" if safe else "FAIL",
        "safe": safe,
        "accepted_count": result.get("replay", {}).get("accepted_count", 0),
        "payload_count": result.get("payloads", {}).get("payload_count", 0),
        "warnings": warnings,
    }

from __future__ import annotations

from sandbox_read_only_fault_injection.fault_schema_validator import validate_all_fault_schemas
from sandbox_read_only_mock_replay.read_only_schema_validator import validate_all_read_only_schemas
from sandbox_read_only_stability_gate.init import boundary


def check_schema_stability(provider: str = "alpaca") -> dict:
    normal = validate_all_read_only_schemas(provider)
    faults = validate_all_fault_schemas(provider)
    checks = {
        "account_schema_placeholder_only": normal.get("schema_valid") is True,
        "balance_schema_redacted_only": normal.get("schema_valid") is True,
        "position_schema_redacted_only": normal.get("schema_valid") is True,
        "malformed_snapshots_rejected": faults.get("schema_faults_detected") is True,
        "missing_timestamp_detected": "missing timestamp placeholder" in faults.get("findings", []),
        "missing_account_ref_detected": "missing account_ref placeholder" in faults.get("findings", []),
        "raw_payload_storage_rejected": "raw_payload_stored true" in faults.get("findings", []),
        "provider_payload_unredacted_rejected": "provider_payload_redacted false" in faults.get("findings", []),
    }
    stable = all(checks.values())
    return {
        **boundary(),
        "provider": provider,
        "schema_stable": stable,
        "findings": [] if stable else ["schema stability incomplete"],
        "warnings": [] if stable else ["schema stability warning"],
    }

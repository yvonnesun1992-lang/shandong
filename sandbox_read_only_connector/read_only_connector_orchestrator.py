from __future__ import annotations

from sandbox_read_only_connector.account_snapshot_schema import build_account_snapshot_schema
from sandbox_read_only_connector.balance_snapshot_schema import build_balance_snapshot_schema
from sandbox_read_only_connector.init import boundary
from sandbox_read_only_connector.position_snapshot_schema import build_position_snapshot_schema
from sandbox_read_only_connector.read_only_audit_policy import build_read_only_audit_policy
from sandbox_read_only_connector.read_only_credential_scope import build_read_only_credential_scope
from sandbox_read_only_connector.read_only_rate_limit_policy import build_read_only_rate_limit_policy
from sandbox_read_only_connector.read_only_redaction_policy import build_redaction_policy
from sandbox_read_only_connector.read_only_safety_validator import build_read_only_safety_summary, validate_read_only_safety
from sandbox_read_only_connector.read_only_scope_definition import build_read_only_scope_definition


def build_read_only_connector_blueprint(provider: str = "alpaca") -> dict:
    result = {
        **boundary(),
        "provider": provider,
        "scope": build_read_only_scope_definition(provider),
        "credential_scope": build_read_only_credential_scope(provider),
        "account_schema": build_account_snapshot_schema(provider),
        "balance_schema": build_balance_snapshot_schema(provider),
        "position_schema": build_position_snapshot_schema(provider),
        "redaction": build_redaction_policy(provider),
        "rate_limit": build_read_only_rate_limit_policy(provider),
        "audit": build_read_only_audit_policy(provider),
        "safety": build_read_only_safety_summary(),
    }
    result["self_validation"] = validate_read_only_safety(result)
    return result


def summarize_read_only_connector_blueprint(result: dict) -> dict:
    warnings = []
    warnings.extend(result.get("safety", {}).get("warnings", []))
    warnings.extend(result.get("self_validation", {}).get("warnings", []))
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "verdict": "WARNING" if warnings else "PASS",
        "read_only_runtime_enabled": False,
        "sandbox_api_enabled": False,
        "account_read_enabled": False,
        "position_read_enabled": False,
        "balance_read_enabled": False,
        "order_submission_enabled": False,
        "safe": result.get("safety", {}).get("safe", False) and result.get("self_validation", {}).get("safe", False),
        "warnings": warnings,
    }

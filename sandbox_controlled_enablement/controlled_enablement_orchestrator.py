from __future__ import annotations

from sandbox_controlled_enablement.account_read_enablement_conditions import build_account_read_enablement_conditions
from sandbox_controlled_enablement.controlled_enablement_conditions import build_controlled_enablement_conditions
from sandbox_controlled_enablement.controlled_enablement_decision_record import build_controlled_enablement_decision
from sandbox_controlled_enablement.controlled_enablement_safety_validator import (
    build_controlled_enablement_safety_summary,
    validate_controlled_enablement_safety,
)
from sandbox_controlled_enablement.emergency_stop_conditions import build_emergency_stop_conditions
from sandbox_controlled_enablement.feature_flag_dependency_graph import build_feature_flag_dependency_graph
from sandbox_controlled_enablement.init import boundary
from sandbox_controlled_enablement.order_preview_enablement_conditions import build_order_preview_enablement_conditions
from sandbox_controlled_enablement.order_submission_blocker import build_order_submission_blocker
from sandbox_controlled_enablement.sandbox_api_enablement_conditions import build_sandbox_api_enablement_conditions
from sandbox_controlled_enablement.secret_read_enablement_conditions import build_secret_read_enablement_conditions
from sandbox_controlled_enablement.staged_unlock_plan import build_staged_unlock_plan


def build_controlled_enablement_blueprint(provider: str = "alpaca") -> dict:
    result = {
        **boundary(),
        "provider": provider,
        "conditions": build_controlled_enablement_conditions(provider),
        "staged_unlock_plan": build_staged_unlock_plan(provider),
        "feature_flags": build_feature_flag_dependency_graph(provider),
        "secret_read": build_secret_read_enablement_conditions(provider),
        "sandbox_api": build_sandbox_api_enablement_conditions(provider),
        "account_read": build_account_read_enablement_conditions(provider),
        "order_preview": build_order_preview_enablement_conditions(provider),
        "order_submission_blocker": build_order_submission_blocker(provider),
        "emergency_stop": build_emergency_stop_conditions(provider),
        "decision": build_controlled_enablement_decision(provider),
        "safety": build_controlled_enablement_safety_summary(),
    }
    result["self_validation"] = validate_controlled_enablement_safety(result)
    return result


def summarize_controlled_enablement_blueprint(result: dict) -> dict:
    warnings = []
    warnings.extend(result.get("staged_unlock_plan", {}).get("warnings", []))
    warnings.extend(result.get("safety", {}).get("warnings", []))
    warnings.extend(result.get("self_validation", {}).get("warnings", []))
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "verdict": "WARNING" if warnings else "PASS",
        "decision": result.get("decision", {}).get("decision", "CONTROLLED_GO_BLOCKED"),
        "controlled_go_enabled": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "order_preview_enabled": False,
        "order_submission_enabled": False,
        "safe": result.get("safety", {}).get("safe", False) and result.get("self_validation", {}).get("safe", False),
        "warnings": warnings,
    }

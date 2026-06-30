from __future__ import annotations

from sandbox_dry_run_launch.dry_run_rollback_plan import build_dry_run_rollback_plan
from sandbox_dry_run_launch.dry_run_scope_definition import build_dry_run_scope_definition
from sandbox_dry_run_launch.feature_flag_launch_plan import build_feature_flag_launch_plan
from sandbox_dry_run_launch.go_no_go_gate import build_go_no_go_summary
from sandbox_dry_run_launch.init import boundary
from sandbox_dry_run_launch.launch_audit_trail import build_launch_audit_trail
from sandbox_dry_run_launch.launch_safety_validator import build_launch_safety_summary
from sandbox_dry_run_launch.launch_sequence_plan import build_launch_sequence_plan
from sandbox_dry_run_launch.preflight_checklist import build_preflight_checklist
from sandbox_dry_run_launch.responsibility_matrix import build_responsibility_matrix


def build_dry_run_launch_plan(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "scope": build_dry_run_scope_definition(provider),
        "feature_flags": build_feature_flag_launch_plan(provider),
        "responsibility": build_responsibility_matrix(provider),
        "preflight": build_preflight_checklist(provider),
        "sequence": build_launch_sequence_plan(provider),
        "rollback": build_dry_run_rollback_plan(provider),
        "gate": build_go_no_go_summary(provider),
        "audit": build_launch_audit_trail(provider),
        "safety": build_launch_safety_summary(),
    }


def summarize_dry_run_launch_plan(result: dict) -> dict:
    warnings = []
    warnings.extend(result.get("gate", {}).get("warnings", []))
    warnings.extend(result.get("preflight", {}).get("warnings", []))
    warnings.extend(result.get("safety", {}).get("warnings", []))
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "verdict": "WARNING" if warnings else "PASS",
        "gate": result.get("gate", {}).get("gate", "NO_GO"),
        "preflight_ready": result.get("preflight", {}).get("preflight_ready", False),
        "safe": result.get("safety", {}).get("safe", False),
        "warnings": warnings,
    }

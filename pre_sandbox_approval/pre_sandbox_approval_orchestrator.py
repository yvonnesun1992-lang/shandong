from __future__ import annotations

from pre_sandbox_approval.approval_audit_trail import build_approval_audit_trail
from pre_sandbox_approval.approval_gate_evaluator import build_approval_gate_summary
from pre_sandbox_approval.approval_request_schema import build_approval_request_schema
from pre_sandbox_approval.approval_safety_validator import build_approval_safety_summary
from pre_sandbox_approval.evidence_requirement_validator import validate_evidence_requirements
from pre_sandbox_approval.init import boundary
from pre_sandbox_approval.operator_role_policy import build_operator_role_policy
from pre_sandbox_approval.risk_acknowledgement_policy import build_risk_acknowledgement_policy


def run_pre_sandbox_approval_review(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "approval_request_schema": build_approval_request_schema(provider),
        "evidence": validate_evidence_requirements(provider),
        "operator_roles": build_operator_role_policy(),
        "risk_acknowledgement": build_risk_acknowledgement_policy(),
        "approval_gate": build_approval_gate_summary(provider),
        "audit_trail": build_approval_audit_trail(provider),
        "safety": build_approval_safety_summary(),
    }


def summarize_approval_review(result: dict) -> dict:
    warnings = []
    if result.get("evidence", {}).get("evidence_ready") is False:
        warnings.append("evidence requirements are listed but sandbox entry remains blocked")
    warnings.extend(result.get("approval_gate", {}).get("warnings", []))
    warnings.extend(result.get("safety", {}).get("warnings", []))
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "verdict": "WARNING" if warnings else "PASS",
        "approval_gate": result.get("approval_gate", {}).get("approval_gate", "BLOCKED"),
        "evidence_ready": result.get("evidence", {}).get("evidence_ready", False),
        "safe": result.get("safety", {}).get("safe", False),
        "warnings": warnings,
    }

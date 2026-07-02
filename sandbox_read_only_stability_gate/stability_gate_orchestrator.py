from __future__ import annotations

from sandbox_read_only_stability_gate.audit_stability_check import check_audit_stability
from sandbox_read_only_stability_gate.fault_evidence_collector import collect_fault_evidence
from sandbox_read_only_stability_gate.init import boundary
from sandbox_read_only_stability_gate.order_path_stability_check import check_order_path_stability
from sandbox_read_only_stability_gate.redaction_stability_check import check_redaction_stability
from sandbox_read_only_stability_gate.replay_evidence_collector import collect_replay_evidence
from sandbox_read_only_stability_gate.schema_stability_check import check_schema_stability
from sandbox_read_only_stability_gate.stability_gate_decision import build_stability_gate_decision
from sandbox_read_only_stability_gate.stability_gate_safety_validator import build_stability_gate_safety_summary


def run_read_only_stability_gate(provider: str = "alpaca") -> dict:
    replay = collect_replay_evidence(provider)
    fault = collect_fault_evidence(provider)
    redaction = check_redaction_stability(provider)
    schema = check_schema_stability(provider)
    audit = check_audit_stability(provider)
    order = check_order_path_stability(provider)
    decision = build_stability_gate_decision(provider)
    safety = build_stability_gate_safety_summary()
    return {
        **boundary(),
        "provider": provider,
        "replay": replay,
        "fault": fault,
        "redaction": redaction,
        "schema": schema,
        "audit": audit,
        "order_path": order,
        "decision_record": decision,
        "safety": safety,
    }


def summarize_stability_gate(result: dict) -> dict:
    warnings = []
    errors = []
    for key in ["replay", "fault", "redaction", "schema", "audit", "order_path", "decision_record", "safety"]:
        warnings.extend(result.get(key, {}).get("warnings", []))
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "replay_evidence_ready": result.get("replay", {}).get("replay_evidence_ready", False),
        "fault_evidence_ready": result.get("fault", {}).get("fault_evidence_ready", False),
        "redaction_stable": result.get("redaction", {}).get("redaction_stable", False),
        "schema_stable": result.get("schema", {}).get("schema_stable", False),
        "audit_stable": result.get("audit", {}).get("audit_stable", False),
        "order_path_stable": result.get("order_path", {}).get("order_path_stable", False),
        "order_path_blocked": result.get("order_path", {}).get("order_path_blocked", True),
        "decision": "STABILITY_GATE_BLOCKED",
        "stability_gate_passed": False,
        "read_only_connector_allowed": False,
        "errors": errors,
        "warnings": warnings,
        "verdict": "WARNING" if warnings else "PASS",
    }

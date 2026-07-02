from __future__ import annotations

from sandbox_read_only_evidence_pack.audit_evidence_pack import build_audit_evidence_pack
from sandbox_read_only_evidence_pack.evidence_completeness_check import check_evidence_completeness
from sandbox_read_only_evidence_pack.evidence_pack_decision import build_evidence_pack_decision
from sandbox_read_only_evidence_pack.evidence_pack_safety_validator import build_evidence_pack_safety_summary
from sandbox_read_only_evidence_pack.evidence_source_collector import collect_evidence_sources
from sandbox_read_only_evidence_pack.init import boundary
from sandbox_read_only_evidence_pack.order_blocking_evidence_pack import build_order_blocking_evidence_pack
from sandbox_read_only_evidence_pack.redaction_evidence_pack import build_redaction_evidence_pack
from sandbox_read_only_evidence_pack.safety_boundary_evidence_pack import build_safety_boundary_evidence_pack
from sandbox_read_only_evidence_pack.schema_evidence_pack import build_schema_evidence_pack


def build_read_only_evidence_pack(provider: str = "alpaca") -> dict:
    sources = collect_evidence_sources(provider)
    completeness = check_evidence_completeness(provider)
    redaction = build_redaction_evidence_pack(provider)
    schema = build_schema_evidence_pack(provider)
    audit = build_audit_evidence_pack(provider)
    order = build_order_blocking_evidence_pack(provider)
    safety_boundary = build_safety_boundary_evidence_pack(provider)
    decision = build_evidence_pack_decision(provider)
    safety = build_evidence_pack_safety_summary()
    return {
        **boundary(),
        "provider": provider,
        "sources": sources,
        "completeness": completeness,
        "redaction": redaction,
        "schema": schema,
        "audit": audit,
        "order_blocking": order,
        "safety_boundary": safety_boundary,
        "decision_record": decision,
        "safety": safety,
    }


def summarize_read_only_evidence_pack(result: dict) -> dict:
    warnings: list[str] = []
    errors: list[str] = []
    for key in [
        "sources",
        "completeness",
        "redaction",
        "schema",
        "audit",
        "order_blocking",
        "safety_boundary",
        "decision_record",
        "safety",
    ]:
        warnings.extend(result.get(key, {}).get("warnings", []))
        errors.extend(result.get(key, {}).get("errors", []))
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "source_count": result.get("sources", {}).get("source_count", 0),
        "evidence_complete": result.get("completeness", {}).get("evidence_complete", False),
        "redaction_evidence_ready": result.get("redaction", {}).get("redaction_evidence_ready", False),
        "schema_evidence_ready": result.get("schema", {}).get("schema_evidence_ready", False),
        "audit_evidence_ready": result.get("audit", {}).get("audit_evidence_ready", False),
        "order_blocking_evidence_ready": result.get("order_blocking", {}).get("order_blocking_evidence_ready", False),
        "safety_evidence_ready": result.get("safety_boundary", {}).get("safety_evidence_ready", False),
        "evidence_pack_passed": False,
        "read_only_connector_allowed": False,
        "decision": "READ_ONLY_EVIDENCE_ONLY",
        "errors": errors,
        "warnings": warnings,
        "verdict": "FAIL" if errors else ("WARNING" if warnings else "PASS"),
    }


from __future__ import annotations

from sandbox_preflight_packet.artifact_manifest import build_artifact_manifest, validate_artifact_manifest
from sandbox_preflight_packet.blocking_item_register import build_blocking_item_register
from sandbox_preflight_packet.final_decision_record import build_final_preflight_decision
from sandbox_preflight_packet.final_preflight_checklist import build_final_preflight_checklist
from sandbox_preflight_packet.init import boundary
from sandbox_preflight_packet.preflight_audit_trail import build_preflight_audit_trail
from sandbox_preflight_packet.preflight_evidence_digest import build_preflight_evidence_digest
from sandbox_preflight_packet.preflight_safety_validator import build_preflight_safety_summary


def build_preflight_packet(provider: str = "alpaca") -> dict:
    manifest = build_artifact_manifest(provider)
    return {
        **boundary(),
        "provider": provider,
        "checklist": build_final_preflight_checklist(provider),
        "artifact_manifest": manifest,
        "artifact_validation": validate_artifact_manifest(manifest),
        "blocking_items": build_blocking_item_register(provider),
        "evidence_digest": build_preflight_evidence_digest(provider),
        "decision": build_final_preflight_decision(provider),
        "audit": build_preflight_audit_trail(provider),
        "safety": build_preflight_safety_summary(),
    }


def summarize_preflight_packet(result: dict) -> dict:
    warnings = []
    warnings.extend(result.get("checklist", {}).get("warnings", []))
    warnings.extend(result.get("evidence_digest", {}).get("warnings", []))
    warnings.extend(result.get("safety", {}).get("warnings", []))
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "verdict": "WARNING" if warnings else "PASS",
        "decision": result.get("decision", {}).get("decision", "NO_GO"),
        "preflight_ready": False,
        "sandbox_dry_run_blocked": True,
        "safe": result.get("safety", {}).get("safe", False),
        "warnings": warnings,
    }

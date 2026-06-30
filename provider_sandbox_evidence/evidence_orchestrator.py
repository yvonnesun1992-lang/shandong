from __future__ import annotations

from provider_sandbox_evidence import boundary
from provider_sandbox_evidence.evidence_safety_validator import build_evidence_safety_summary
from provider_sandbox_evidence.evidence_source_collector import collect_evidence_sources
from provider_sandbox_evidence.fault_evidence_summary import build_fault_evidence_summary
from provider_sandbox_evidence.readiness_gap_analyzer import analyze_readiness_gaps
from provider_sandbox_evidence.replay_evidence_summary import build_replay_evidence_summary
from provider_sandbox_evidence.sandbox_entry_gate import evaluate_sandbox_entry_gate
from provider_sandbox_evidence.soak_evidence_summary import build_soak_evidence_summary


def build_sandbox_readiness_evidence_pack(provider: str) -> dict:
    return {
        "provider": provider,
        "sources": collect_evidence_sources(provider),
        "replay": build_replay_evidence_summary(provider),
        "fault": build_fault_evidence_summary(provider),
        "soak": build_soak_evidence_summary(provider),
        "gaps": analyze_readiness_gaps(provider),
        "gate": evaluate_sandbox_entry_gate(provider),
        "safety": build_evidence_safety_summary(),
        **boundary(),
    }


def summarize_evidence_pack(result: dict) -> dict:
    warnings = ["sandbox entry remains blocked by design"]
    errors = [] if result["safety"]["safe"] else result["safety"]["errors"]
    verdict = "FAIL" if errors else "WARNING"
    return {
        "provider": result["provider"],
        "ready_for_sandbox_api": False,
        "ready_for_sandbox_orders": False,
        "blocking_gaps": result["gaps"]["blocking_gaps"],
        "warnings": warnings,
        "errors": errors,
        "verdict": verdict,
        **boundary(),
    }

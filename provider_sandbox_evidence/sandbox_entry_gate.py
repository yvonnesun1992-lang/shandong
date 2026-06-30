from __future__ import annotations

from provider_sandbox_evidence import boundary
from provider_sandbox_evidence.readiness_gap_analyzer import analyze_readiness_gaps


def evaluate_sandbox_entry_gate(provider: str) -> dict:
    gaps = analyze_readiness_gaps(provider)
    return {
        "provider": provider,
        "gate": "BLOCKED",
        "ready_for_sandbox_api": False,
        "ready_for_sandbox_orders": False,
        "blocking_items": gaps["blocking_gaps"],
        "warnings": ["V5.26 is evidence pack only; sandbox entry is blocked"],
        **boundary(),
    }


def build_sandbox_entry_gate_summary(provider: str) -> dict:
    return evaluate_sandbox_entry_gate(provider)

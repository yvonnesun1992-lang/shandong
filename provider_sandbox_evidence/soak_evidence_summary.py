from __future__ import annotations

from provider_sandbox_evidence import boundary


def build_soak_evidence_summary(provider: str) -> dict:
    items = [
        "soak scenarios covered",
        "stability metrics",
        "stability gate",
        "coverage validation",
        "safety validation",
        "audit coverage",
        "error budget",
    ]
    return {"provider": provider, "soak_evidence_ready": True, "evidence_items": items, "blocking_items": [], "warnings": [], **boundary()}

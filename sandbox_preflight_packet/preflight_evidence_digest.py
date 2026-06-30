from __future__ import annotations

from sandbox_preflight_packet.init import boundary


def build_preflight_evidence_digest(provider: str = "alpaca") -> dict:
    digest_items = [
        {"name": "replay evidence status", "status": "local evidence present or pending review"},
        {"name": "fault injection evidence status", "status": "local evidence present or pending review"},
        {"name": "soak stability status", "status": "local evidence present or pending review"},
        {"name": "sandbox readiness evidence status", "status": "pending human review"},
        {"name": "vault design status", "status": "design only"},
        {"name": "approval gate status", "status": "blocked"},
        {"name": "launch plan status", "status": "NO_GO"},
        {"name": "review board status", "status": "NO_GO"},
        {"name": "remaining gaps", "status": "blocking items remain"},
        {"name": "final decision", "status": "NO_GO"},
    ]
    return {
        **boundary(),
        "provider": provider,
        "evidence_digest_ready": False,
        "digest_items": digest_items,
        "final_decision": "NO_GO",
        "warnings": ["evidence digest is not ready for sandbox dry-run"],
    }

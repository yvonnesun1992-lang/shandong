from __future__ import annotations

from sandbox_read_only_evidence_pack.init import boundary

AUDIT_ITEMS = [
    "mock replay audit events generated",
    "audit events placeholder-only",
    "raw payload not logged",
    "values not logged",
    "account_ref placeholder-only",
    "order_submitted false",
    "audit write failure simulated",
    "audit fallback written",
    "audit failure escalated as warning or error",
]


def build_audit_evidence_pack(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "audit_evidence_ready": True,
        "audit_evidence_items": AUDIT_ITEMS,
        "unresolved_audit_gaps": [],
        "warnings": [],
    }


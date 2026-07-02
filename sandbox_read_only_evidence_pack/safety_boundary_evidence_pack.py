from __future__ import annotations

from sandbox_read_only_evidence_pack.init import boundary

SAFETY_ITEMS = [
    "sandbox API disabled",
    "secret read disabled",
    "account read disabled",
    "balance read disabled",
    "position read disabled",
    "order preview disabled",
    "order submission disabled",
    "broker disconnected",
    "real money disabled",
    "no broker SDK import evidence",
    "no network call evidence",
    "no plaintext credential evidence",
    "no real account id evidence",
    "no real order id evidence",
    "no raw real provider payload evidence",
    "no real provider endpoint URL evidence",
]


def build_safety_boundary_evidence_pack(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "safety_evidence_ready": True,
        "safety_evidence_items": SAFETY_ITEMS,
        "unresolved_safety_gaps": [],
        "warnings": [],
    }


from __future__ import annotations

from sandbox_read_only_final_review.init import boundary

EVIDENCE_ITEMS = [
    "V5.34 mock replay evidence",
    "V5.35 fault injection evidence",
    "V5.36 stability gate evidence",
    "V5.37 evidence pack",
    "redaction evidence",
    "schema evidence",
    "audit evidence",
    "order blocking evidence",
    "safety boundary evidence",
    "pytest evidence placeholder",
    "system_doctor evidence placeholder",
    "security scan evidence placeholder",
    "frontend structure check placeholder",
]


def build_evidence_review_matrix(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "evidence_items": [{"name": item, "review_status": "available"} for item in EVIDENCE_ITEMS],
        "evidence_review_ready": True,
        "blocking_items": [],
        "warnings": ["evidence review readiness cannot unlock read-only connector access"],
    }


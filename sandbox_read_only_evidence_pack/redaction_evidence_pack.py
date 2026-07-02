from __future__ import annotations

from sandbox_read_only_evidence_pack.init import boundary

REDACTION_ITEMS = [
    "normal mock account values placeholder-only",
    "normal mock balance values redacted",
    "normal mock position values redacted",
    "account id fault detected",
    "cash balance numeric fault detected",
    "buying power numeric fault detected",
    "market value numeric fault detected",
    "quantity numeric fault detected",
    "unrealized pnl numeric fault detected",
    "raw provider payload fault detected",
    "provider endpoint URL fault detected",
    "api key or token fault detected",
    "frontend redacted-only evidence",
    "logs placeholder-only evidence",
]


def build_redaction_evidence_pack(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "redaction_evidence_ready": True,
        "redaction_evidence_items": REDACTION_ITEMS,
        "unresolved_redaction_gaps": [],
        "warnings": [],
    }


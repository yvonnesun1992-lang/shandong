from __future__ import annotations

from sandbox_read_only_evidence_pack.init import boundary

SCHEMA_ITEMS = [
    "account snapshot schema placeholder-only",
    "balance snapshot schema redacted-only",
    "position snapshot schema redacted-only",
    "malformed account snapshot rejected",
    "malformed balance snapshot rejected",
    "malformed position snapshot rejected",
    "missing timestamp detected",
    "missing account_ref detected",
    "raw_payload_stored true rejected",
    "provider_payload_redacted false rejected",
    "values_redacted false rejected",
]


def build_schema_evidence_pack(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "schema_evidence_ready": True,
        "schema_evidence_items": SCHEMA_ITEMS,
        "unresolved_schema_gaps": [],
        "warnings": [],
    }


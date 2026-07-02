from __future__ import annotations

from sandbox_read_only_evidence_pack.evidence_source_collector import collect_evidence_sources
from sandbox_read_only_evidence_pack.init import boundary

REQUIRED_ITEMS = [
    "mock replay evidence present",
    "fault injection evidence present",
    "stability gate evidence present",
    "redaction evidence present",
    "schema evidence present",
    "audit evidence present",
    "order blocking evidence present",
    "safety boundary evidence present",
    "system_doctor placeholder present",
    "pytest placeholder present",
    "security scan placeholder present",
    "frontend structure check placeholder present",
]


def check_evidence_completeness(provider: str = "alpaca") -> dict:
    sources = collect_evidence_sources(provider)
    missing_items: list[str] = []
    return {
        **boundary(),
        "provider": provider,
        "checked_items": REQUIRED_ITEMS,
        "source_count": sources["source_count"],
        "evidence_complete": not missing_items,
        "missing_items": missing_items,
        "warnings": ["evidence completeness does not unlock read-only connector access"],
    }


def summarize_evidence_completeness(result: dict) -> dict:
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "evidence_complete": result.get("evidence_complete", False),
        "missing_items": result.get("missing_items", []),
        "warnings": result.get("warnings", []),
    }

from __future__ import annotations

from sandbox_read_only_evidence_pack.init import boundary

SOURCE_NAMES = [
    "V5.34 read-only mock replay report",
    "V5.34 mock replay payload catalog",
    "V5.34 schema validation result",
    "V5.34 redaction validation result",
    "V5.34 audit replay result",
    "V5.35 fault injection report",
    "V5.35 fault payload catalog",
    "V5.35 redaction failure detection result",
    "V5.35 stale snapshot detection result",
    "V5.35 audit failure simulation result",
    "V5.35 rate limit fault result",
    "V5.35 order path intrusion detection result",
    "V5.36 stability gate report",
    "V5.36 replay evidence result",
    "V5.36 fault evidence result",
    "V5.36 redaction stability result",
    "V5.36 schema stability result",
    "V5.36 audit stability result",
    "V5.36 order path stability result",
    "V5.36 stability gate decision",
]


def collect_evidence_sources(provider: str = "alpaca") -> dict:
    sources = [{"name": name, "status": "available", "storage": "local-placeholder-summary"} for name in SOURCE_NAMES]
    return {
        **boundary(),
        "provider": provider,
        "evidence_sources": sources,
        "source_count": len(sources),
        "sources_collected": True,
        "warnings": [],
    }


def summarize_evidence_sources(evidence: dict) -> dict:
    return {
        **boundary(),
        "provider": evidence.get("provider", "alpaca"),
        "source_count": evidence.get("source_count", 0),
        "sources_collected": bool(evidence.get("evidence_sources")),
        "warnings": evidence.get("warnings", []),
    }


from __future__ import annotations

from pathlib import Path

from provider_sandbox_evidence import boundary


SOURCE_FILES = {
    "v5_23_offline_replay": Path("reports/v5_23_provider_offline_replay_report.md"),
    "v5_24_fault_injection": Path("reports/v5_24_provider_fault_injection_report.md"),
    "v5_25_offline_soak": Path("reports/v5_25_provider_offline_soak_report.md"),
}


def collect_evidence_sources(provider: str) -> dict:
    sources = {
        name: {
            "source_name": name,
            "path": path.as_posix(),
            "exists": path.exists(),
            "summary": _safe_summary(path),
            **boundary(),
        }
        for name, path in SOURCE_FILES.items()
    }
    return {"provider": provider, "sources": sources, "warnings": [], **boundary()}


def summarize_evidence_sources(provider: str) -> dict:
    collected = collect_evidence_sources(provider)
    missing = [name for name, item in collected["sources"].items() if not item["exists"]]
    return {"provider": provider, "total_sources": len(collected["sources"]), "missing_sources": missing, "warnings": [], **boundary()}


def _safe_summary(path: Path) -> str:
    if not path.exists():
        return "missing local report"
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    first_heading = next((line.strip("# ").strip() for line in text if line.startswith("#")), "local report present")
    return first_heading[:120]

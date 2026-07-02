from __future__ import annotations

from pathlib import Path

from sandbox_read_only_evidence_pack.evidence_pack_orchestrator import (
    build_read_only_evidence_pack,
    summarize_read_only_evidence_pack,
)

REPORT_PATH = Path("reports/v5_37_sandbox_read_only_evidence_pack_report.md")


def generate_sandbox_read_only_evidence_pack_report(provider: str = "alpaca", check: str = "all") -> dict:
    pack = build_read_only_evidence_pack(provider)
    summary = summarize_read_only_evidence_pack(pack)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V5.37 Sandbox Read-Only Connector Evidence Pack",
        "",
        f"- Mode: read-only evidence pack only",
        f"- Provider: {provider}",
        f"- Check: {check}",
        f"- Verdict: {summary['verdict']}",
        f"- Decision: {summary['decision']}",
        f"- Source count: {summary['source_count']}",
        f"- Evidence complete: {summary['evidence_complete']}",
        f"- Evidence pack passed: {summary['evidence_pack_passed']}",
        f"- Read-only connector allowed: {summary['read_only_connector_allowed']}",
        "",
        "## Evidence",
        "",
        "- V5.34 mock replay evidence summarized",
        "- V5.35 fault injection evidence summarized",
        "- V5.36 stability gate evidence summarized",
        "- Redaction, schema, audit, order blocking, and safety boundary evidence summarized",
        "",
        "## Safety Boundary",
        "",
        "- Current stage is read-only evidence pack only",
        "- No real broker connection",
        "- No sandbox API connection",
        "- No credential or secret read",
        "- No account, balance, or position read",
        "- No order preview or order submission",
        "- No real funds or production trading",
        "",
        "## Missing Production Requirements",
        "",
        "- Operator approval for any future real connector work",
        "- External security review before real credentials",
        "- Explicit separate release for any sandbox API connection",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        **summary,
        "path": str(REPORT_PATH),
        "report_written": True,
        "check": check,
    }


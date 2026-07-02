from __future__ import annotations

from pathlib import Path

from sandbox_read_only_final_review.final_review_orchestrator import build_read_only_final_review, summarize_read_only_final_review

REPORT_PATH = Path("reports/v5_38_sandbox_read_only_final_review_report.md")


def generate_sandbox_read_only_final_review_report(provider: str = "alpaca", check: str = "all") -> dict:
    review = build_read_only_final_review(provider)
    summary = summarize_read_only_final_review(review)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V5.38 Sandbox Read-Only Connector Final Review Board",
        "",
        "- Mode: read-only final review board only",
        f"- Provider: {provider}",
        f"- Check: {check}",
        f"- Verdict: {summary['verdict']}",
        f"- Decision: {summary['decision']}",
        f"- Evidence review ready: {summary['evidence_review_ready']}",
        f"- Risk acceptance ready: {summary['risk_acceptance_ready']}",
        f"- Missing requirement count: {summary['missing_count']}",
        f"- Final review passed: {summary['final_review_passed']}",
        f"- Read-only connector allowed: {summary['read_only_connector_allowed']}",
        "",
        "## Review Inputs",
        "",
        "- V5.34 mock replay evidence",
        "- V5.35 fault injection evidence",
        "- V5.36 stability gate evidence",
        "- V5.37 evidence pack",
        "",
        "## Safety Boundary",
        "",
        "- Current stage is read-only final review board only",
        "- No real broker connection",
        "- No sandbox API connection",
        "- No credential or secret read",
        "- No account, balance, or position read",
        "- No order preview or order submission",
        "- No real funds or production trading",
        "",
        "## Missing Production Requirements",
        "",
        "- Live credential vault",
        "- Sandbox account credentials",
        "- Independent provider documentation verification",
        "- Compliance signoff",
        "- Operator training",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {**summary, "path": str(REPORT_PATH), "report_written": True, "check": check}


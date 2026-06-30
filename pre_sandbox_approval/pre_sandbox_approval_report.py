from __future__ import annotations

from pathlib import Path

from config.v5_pre_sandbox_approval_config import get_pre_sandbox_approval_provider
from pre_sandbox_approval.pre_sandbox_approval_orchestrator import run_pre_sandbox_approval_review, summarize_approval_review


REPORT_PATH = Path("reports/v5_28_pre_sandbox_approval_report.md")


def generate_pre_sandbox_approval_report(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_pre_sandbox_approval_provider()
    review = run_pre_sandbox_approval_review(selected)
    summary = summarize_approval_review(review)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(review, summary, check), encoding="utf-8")
    return {
        **summary,
        "path": REPORT_PATH.as_posix(),
        "check": check,
    }


def _render_report(review: dict, summary: dict, check: str) -> str:
    lines = [
        "# V5.28 Pre-Sandbox Operator Approval Gate",
        "",
        f"Final verdict: {summary['verdict']}",
        "",
        "Current phase is pre-sandbox approval gate design only.",
        "",
        "Boundary:",
        "- Approval runtime enabled: false",
        "- Operator approval granted: false",
        "- Sandbox API enabled: false",
        "- Secret read enabled: false",
        "- Broker connected: false",
        "- Order submission enabled: false",
        "- Real money enabled: false",
        "- Paper trading: true",
        "",
        "Design areas:",
        "- Approval request schema",
        "- Evidence requirement validation",
        "- Operator role policy",
        "- Risk acknowledgement policy",
        "- Approval gate evaluation",
        "- Approval audit trail",
        "- Safety validation",
        "",
        "Missing production requirements:",
        "- Real provider terms review",
        "- Real market data terms review",
        "- Real credential vault implementation",
        "- Separate production approval system",
        "",
        "This is not a production trading system.",
    ]
    return "\n".join(lines) + "\n"

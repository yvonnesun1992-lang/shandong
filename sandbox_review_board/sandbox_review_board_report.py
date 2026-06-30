from __future__ import annotations

from pathlib import Path

from config.v5_sandbox_review_board_config import get_review_board_provider
from sandbox_review_board.review_board_orchestrator import build_review_board_packet, summarize_review_board_packet


REPORT_PATH = Path("reports/v5_30_sandbox_review_board_report.md")


def generate_sandbox_review_board_report(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_review_board_provider()
    packet = build_review_board_packet(selected)
    summary = summarize_review_board_packet(packet)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(packet, summary), encoding="utf-8")
    return {
        **summary,
        "path": REPORT_PATH.as_posix(),
        "check": check,
    }


def _render_report(packet: dict, summary: dict) -> str:
    return "\n".join(
        [
            "# V5.30 Sandbox Dry-Run Readiness Review Board",
            "",
            f"Final verdict: {summary['verdict']}",
            "",
            "Current phase is sandbox dry-run readiness review board only.",
            "",
            "Boundary:",
            "- Review runtime enabled: false",
            "- Reviewer approval enabled: false",
            "- Sandbox API enabled: false",
            "- Secret read enabled: false",
            "- Account read enabled: false",
            "- Broker connected: false",
            "- Order submission enabled: false",
            "- Real money enabled: false",
            "- Paper trading: true",
            "",
            "Review areas:",
            "- Review board charter",
            "- Reviewer role matrix",
            "- Evidence review matrix",
            "- Risk acceptance matrix",
            "- Readiness score",
            "- Go / No-Go decision record",
            "- Review audit trail",
            "- Safety validation",
            "",
            "Missing production requirements:",
            "- Real provider terms review",
            "- Real credential vault implementation",
            "- Verified provider sandbox account outside this repo",
            "- Independent compliance sign-off",
            "- Immutable audit storage",
            "",
            "This is not a production trading system.",
        ]
    ) + "\n"

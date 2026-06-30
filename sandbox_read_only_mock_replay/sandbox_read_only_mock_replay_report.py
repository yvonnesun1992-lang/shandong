from __future__ import annotations

from pathlib import Path

from config.v5_read_only_mock_replay_config import get_read_only_mock_replay_provider
from sandbox_read_only_mock_replay.read_only_mock_replay_orchestrator import run_read_only_mock_replay, summarize_read_only_mock_replay

REPORT_PATH = Path("reports/v5_34_sandbox_read_only_mock_replay_report.md")


def generate_sandbox_read_only_mock_replay_report(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_read_only_mock_replay_provider()
    result = run_read_only_mock_replay(selected)
    summary = summarize_read_only_mock_replay(result)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(summary), encoding="utf-8")
    return {
        **summary,
        "path": REPORT_PATH.as_posix(),
        "check": check,
    }


def _render_report(summary: dict) -> str:
    return "\n".join(
        [
            "# V5.34 Sandbox Read-Only Connector Mock Replay",
            "",
            f"Final verdict: {summary['verdict']}",
            "",
            "Current phase is read-only mock replay only.",
            "",
            "Boundary:",
            "- Mock replay runtime enabled: false",
            "- Sandbox API enabled: false",
            "- Credential read enabled: false",
            "- Account read enabled: false",
            "- Position read enabled: false",
            "- Balance read enabled: false",
            "- Order preview enabled: false",
            "- Order submission enabled: false",
            "- Broker connected: false",
            "- Real money enabled: false",
            "- Paper trading: true",
            "",
            "Replay areas:",
            "- Local placeholder payload catalog",
            "- Schema validation",
            "- Redaction validation",
            "- Replay runner",
            "- Audit replay",
            "- Safety validation",
            "",
            "No provider network, account lookup, balance lookup, position lookup, order preview, order submission, or raw provider payload is enabled.",
        ]
    ) + "\n"

from __future__ import annotations

from pathlib import Path

from config.v5_sandbox_preflight_packet_config import get_preflight_packet_provider
from sandbox_preflight_packet.preflight_packet_orchestrator import build_preflight_packet, summarize_preflight_packet


REPORT_PATH = Path("reports/v5_31_sandbox_preflight_packet_report.md")


def generate_sandbox_preflight_packet_report(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_preflight_packet_provider()
    packet = build_preflight_packet(selected)
    summary = summarize_preflight_packet(packet)
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
            "# V5.31 Sandbox Dry-Run Final Preflight Packet",
            "",
            f"Final verdict: {summary['verdict']}",
            "",
            "Current phase is sandbox dry-run final preflight packet only.",
            "",
            "Boundary:",
            "- Preflight runtime enabled: false",
            "- Packet approval enabled: false",
            "- Sandbox API enabled: false",
            "- Secret read enabled: false",
            "- Account read enabled: false",
            "- Broker connected: false",
            "- Order submission enabled: false",
            "- Real money enabled: false",
            "- Paper trading: true",
            "",
            "Packet areas:",
            "- Final preflight checklist",
            "- Artifact manifest",
            "- Blocking item register",
            "- Evidence digest",
            "- Final decision record",
            "- Preflight audit trail",
            "- Safety validation",
            "",
            "Missing production requirements:",
            "- Verified provider sandbox account outside this repo",
            "- Real credential vault implementation",
            "- Independent compliance sign-off",
            "- Immutable audit storage",
            "- Real connector kill switch test",
            "",
            "This is not a production trading system.",
        ]
    ) + "\n"

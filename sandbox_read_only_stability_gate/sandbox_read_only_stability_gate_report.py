from __future__ import annotations

from pathlib import Path

from config.v5_read_only_stability_gate_config import get_read_only_stability_gate_provider
from sandbox_read_only_stability_gate.stability_gate_orchestrator import run_read_only_stability_gate, summarize_stability_gate

REPORT_PATH = Path("reports/v5_36_sandbox_read_only_stability_gate_report.md")


def generate_sandbox_read_only_stability_gate_report(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_read_only_stability_gate_provider()
    result = run_read_only_stability_gate(selected)
    summary = summarize_stability_gate(result)
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
            "# V5.36 Sandbox Read-Only Connector Stability Gate",
            "",
            f"Final verdict: {summary['verdict']}",
            "",
            "Current phase is read-only stability gate only.",
            "",
            "Stability gate mode:",
            "- Evidence aggregation only",
            "- Decision remains STABILITY_GATE_BLOCKED",
            "- Stability gate passed: false",
            "- Read-only connector allowed: false",
            "",
            "Evidence:",
            f"- Replay evidence ready: {summary['replay_evidence_ready']}",
            f"- Fault evidence ready: {summary['fault_evidence_ready']}",
            f"- Redaction stable: {summary['redaction_stable']}",
            f"- Schema stable: {summary['schema_stable']}",
            f"- Audit stable: {summary['audit_stable']}",
            f"- Order path stable: {summary['order_path_stable']}",
            f"- Order path blocked: {summary['order_path_blocked']}",
            "",
            "Boundary:",
            "- Stability gate runtime enabled: false",
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
            "Missing production requirements:",
            "- Approved live provider connection",
            "- Approved sandbox account",
            "- Approved credential vault",
            "- Approved immutable audit system",
            "- Separate operator approval gate",
            "",
            "This is not a production trading system.",
        ]
    ) + "\n"

from __future__ import annotations

from pathlib import Path

from config.v5_read_only_fault_injection_config import get_read_only_fault_injection_provider
from sandbox_read_only_fault_injection.fault_injection_orchestrator import (
    run_read_only_fault_injection,
    summarize_fault_injection,
)

REPORT_PATH = Path("reports/v5_35_sandbox_read_only_fault_injection_report.md")


def generate_sandbox_read_only_fault_injection_report(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_read_only_fault_injection_provider()
    result = run_read_only_fault_injection(selected)
    summary = summarize_fault_injection(result)
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
            "# V5.35 Sandbox Read-Only Connector Fault Injection",
            "",
            f"Final verdict: {summary['verdict']}",
            "",
            "Current phase is read-only fault injection only.",
            "",
            "Fault injection mode:",
            "- Local mock fault payloads only",
            "- Fault cases must be blocked or warned",
            f"- Total fault cases: {summary['total_fault_cases']}",
            f"- Blocked fault cases: {summary['blocked_fault_cases']}",
            "",
            "Boundary:",
            "- Fault injection runtime enabled: false",
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
            "Fault areas:",
            "- Fault payload catalog",
            "- Schema fault validation",
            "- Redaction failure detection",
            "- Stale snapshot detection",
            "- Audit failure simulation",
            "- Rate limit fault simulation",
            "- Order path intrusion detection",
            "- Fault injection runner results",
            "- Safety validation",
            "",
            "Missing production requirements:",
            "- Approved live provider connection",
            "- Approved sandbox account",
            "- Approved credential vault",
            "- Approved immutable audit system",
            "",
            "This is not a production trading system.",
        ]
    ) + "\n"

from __future__ import annotations

from pathlib import Path

from config.v5_read_only_connector_config import get_read_only_connector_provider
from sandbox_read_only_connector.read_only_connector_orchestrator import (
    build_read_only_connector_blueprint,
    summarize_read_only_connector_blueprint,
)


REPORT_PATH = Path("reports/v5_33_sandbox_read_only_connector_report.md")


def generate_sandbox_read_only_connector_report(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_read_only_connector_provider()
    blueprint = build_read_only_connector_blueprint(selected)
    summary = summarize_read_only_connector_blueprint(blueprint)
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
            "# V5.33 Sandbox Dry-Run Read-Only Connector Blueprint",
            "",
            f"Final verdict: {summary['verdict']}",
            "",
            "Current phase is read-only connector blueprint only.",
            "",
            "Boundary:",
            "- Read-only runtime enabled: false",
            "- Sandbox API enabled: false",
            "- Credential read enabled: false",
            "- Account read enabled: false",
            "- Position read enabled: false",
            "- Balance read enabled: false",
            "- Order preview enabled: false",
            "- Broker connected: false",
            "- Order submission enabled: false",
            "- Real money enabled: false",
            "- Paper trading: true",
            "",
            "Blueprint areas:",
            "- Read-only scope",
            "- Credential scope",
            "- Account snapshot schema",
            "- Balance snapshot schema",
            "- Position snapshot schema",
            "- Redaction policy",
            "- Rate limit policy",
            "- Audit policy",
            "- Safety validation",
            "",
            "Missing production requirements:",
            "- Future approved read-only sandbox credentials",
            "- Future verified provider documentation",
            "- Future redaction review and immutable audit storage",
            "- Future rate limit settings based on approved provider documentation",
            "",
            "This is not a production trading system.",
        ]
    ) + "\n"

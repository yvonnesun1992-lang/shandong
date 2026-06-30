from __future__ import annotations

from pathlib import Path

from config.v5_controlled_enablement_config import get_controlled_enablement_provider
from sandbox_controlled_enablement.controlled_enablement_orchestrator import (
    build_controlled_enablement_blueprint,
    summarize_controlled_enablement_blueprint,
)


REPORT_PATH = Path("reports/v5_32_sandbox_controlled_enablement_report.md")


def generate_sandbox_controlled_enablement_report(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_controlled_enablement_provider()
    blueprint = build_controlled_enablement_blueprint(selected)
    summary = summarize_controlled_enablement_blueprint(blueprint)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(blueprint, summary), encoding="utf-8")
    return {
        **summary,
        "path": REPORT_PATH.as_posix(),
        "check": check,
    }


def _render_report(blueprint: dict, summary: dict) -> str:
    return "\n".join(
        [
            "# V5.32 Sandbox Dry-Run Controlled Enablement Blueprint",
            "",
            f"Final verdict: {summary['verdict']}",
            "",
            "Current phase is controlled enablement blueprint only.",
            "",
            "Boundary:",
            "- Controlled enablement runtime enabled: false",
            "- Controlled GO enabled: false",
            "- Sandbox API enabled: false",
            "- Secret read enabled: false",
            "- Account read enabled: false",
            "- Order preview enabled: false",
            "- Broker connected: false",
            "- Order submission enabled: false",
            "- Real money enabled: false",
            "- Paper trading: true",
            "",
            "Blueprint areas:",
            "- Controlled enablement conditions",
            "- Staged unlock plan",
            "- Feature flag dependency graph",
            "- Secret read enablement conditions",
            "- Sandbox API enablement conditions",
            "- Account read enablement conditions",
            "- Order preview enablement conditions",
            "- Order submission blocker",
            "- Emergency stop conditions",
            "- Controlled enablement decision",
            "- Safety validation",
            "",
            "Missing production requirements:",
            "- Future authorized review board process",
            "- Live credential vault and immutable audit storage",
            "- Approved sandbox account and provider documentation review",
            "- Read-only scope verification",
            "- Kill switch live test and rollback rehearsal",
            "- Compliance signoff and operator training",
            "",
            "This is not a production trading system.",
        ]
    ) + "\n"

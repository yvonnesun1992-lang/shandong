from __future__ import annotations

from pathlib import Path

from config.v5_sandbox_dry_run_launch_config import get_dry_run_launch_provider
from sandbox_dry_run_launch.dry_run_launch_orchestrator import build_dry_run_launch_plan, summarize_dry_run_launch_plan


REPORT_PATH = Path("reports/v5_29_sandbox_dry_run_launch_report.md")


def generate_sandbox_dry_run_launch_report(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_dry_run_launch_provider()
    plan = build_dry_run_launch_plan(selected)
    summary = summarize_dry_run_launch_plan(plan)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(plan, summary), encoding="utf-8")
    return {
        **summary,
        "path": REPORT_PATH.as_posix(),
        "check": check,
    }


def _render_report(plan: dict, summary: dict) -> str:
    return "\n".join(
        [
            "# V5.29 Sandbox Dry-Run Launch Plan",
            "",
            f"Final verdict: {summary['verdict']}",
            "",
            "Current phase is sandbox dry-run launch plan only.",
            "",
            "Boundary:",
            "- Launch runtime enabled: false",
            "- Sandbox API enabled: false",
            "- Secret read enabled: false",
            "- Account read enabled: false",
            "- Broker connected: false",
            "- Order submission enabled: false",
            "- Real money enabled: false",
            "- Paper trading: true",
            "",
            "Plan areas:",
            "- Dry-run scope",
            "- Feature flag launch plan",
            "- Responsibility matrix",
            "- Preflight checklist",
            "- Launch sequence plan",
            "- Rollback plan",
            "- Go / No-Go gate",
            "- Launch audit trail",
            "- Safety validation",
            "",
            "Missing production requirements:",
            "- Real provider terms review",
            "- Real market data terms review",
            "- Real credential vault implementation",
            "- Separate production approval system",
            "- Provider sandbox account setup outside this repo",
            "",
            "This is not a production trading system.",
        ]
    ) + "\n"

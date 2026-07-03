from __future__ import annotations

from pathlib import Path

from guided_setup.guided_setup_orchestrator import build_guided_setup_wizard
from guided_setup.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "reports" / "v5_43_guided_setup_wizard_report.md"


def generate_guided_setup_report() -> dict:
    wizard = build_guided_setup_wizard()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V5.43 Guided Local Setup Wizard Report",
        "",
        f"- likely blocker: {wizard['likely_blocker']}",
        f"- recommended next step: {wizard['recommended_next_step']}",
        f"- missing requirements: {', '.join(wizard['missing_requirements']) or 'none'}",
        "",
        "## Mac Steps",
        "",
        *[f"- {step['title']}: {step['description']}" for step in wizard["mac_steps"]],
        "",
        "## Windows Steps",
        "",
        *[f"- {step['title']}: {step['description']}" for step in wizard["windows_steps"]],
        "",
        "## Command Blocks",
        "",
        *[f"- {block['title']}: {' && '.join(block['commands'])}" for block in wizard["command_blocks"]],
        "",
        "## Plain Language Explanation",
        "",
        *[f"- {line}" for line in wizard["plain_language_summary"]],
        "",
        "## Safety Boundary",
        "",
        "- Current stage is guided setup wizard only.",
        "- It does not automatically install dependencies.",
        "- It does not automatically access external networks.",
        "- It does not connect to a real broker.",
        "- It does not connect to a sandbox API.",
        "- It does not read secrets.",
        "- It does not read accounts, balances, or positions.",
        "- It does not submit orders.",
        "- It does not connect to real money.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"report_generated": True, "path": "reports/v5_43_guided_setup_wizard_report.md", **boundary()}


def summarize_guided_setup_report(result: dict) -> dict:
    return {"report_generated": result.get("report_generated", False), "path": result.get("path", ""), "warnings": result.get("warnings", []), "errors": result.get("errors", []), **boundary()}

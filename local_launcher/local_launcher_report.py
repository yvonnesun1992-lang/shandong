from __future__ import annotations

from pathlib import Path

from local_launcher.local_launcher_orchestrator import build_local_launcher_plan


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "reports" / "v5_39_local_launcher_report.md"


def generate_local_launcher_report() -> dict:
    plan = build_local_launcher_plan()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V5.39 Local Desktop Launcher Report",
        "",
        f"- launcher mode: local_launcher_only",
        f"- verdict: {plan['verdict']}",
        f"- environment ready: {plan['environment']['environment_ready']}",
        f"- port check ready: {plan['ports']['ports_ready']}",
        f"- backend command: `{' '.join(plan['backend_command'])}`",
        f"- frontend command: `cd web/frontend && {' '.join(plan['frontend_command'])}`",
        f"- browser target: `{plan['browser_target']}`",
        "- Mac users: double click `scripts/start_shandong_mac.command`.",
        "- Windows users: double click `scripts/start_shandong_windows.bat`.",
        "",
        "## Safety Boundary",
        "",
        "- Current package is a local launcher only.",
        "- It is not a formal Mac .app installer.",
        "- It is not a Windows .exe installer.",
        "- It does not connect to a real broker.",
        "- It does not connect to a sandbox API.",
        "- It does not read secrets.",
        "- It does not read accounts, balances, or positions.",
        "- It does not submit orders.",
        "- It does not connect to real money.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"path": "reports/v5_39_local_launcher_report.md", "verdict": plan["verdict"], "local_launcher_only": True, "plan": plan}

from __future__ import annotations

from pathlib import Path

from local_run_doctor.init import boundary
from local_run_doctor.local_run_doctor_orchestrator import run_local_run_doctor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "reports" / "v5_42_local_run_doctor_report.md"


def generate_local_run_doctor_report() -> dict:
    result = run_local_run_doctor()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V5.42 Local Run Doctor Report",
        "",
        f"- command availability: python={result['python_available']}, node={result['node_available']}, pnpm={result['pnpm_available']}",
        f"- port diagnosis: frontend_3000={result['frontend_port_open']}, backend_8000={result['backend_port_open']}",
        f"- backend diagnosis: ready={result['backend_ready']}",
        f"- frontend diagnosis: ready={result['frontend_ready']}",
        "- browser targets: localhost only",
        f"- likely reason 3000 not open: {result['likely_reason_3000_not_open']}",
        "",
        "## Recommended Next Steps",
        "",
        *[f"- {step}" for step in result.get("recommended_next_steps", [])],
        "",
        "## Mac Fix Guide",
        "",
        *[f"- {step}" for step in result["fix_guide"]["mac_fix_guide"]],
        "",
        "## Windows Fix Guide",
        "",
        *[f"- {step}" for step in result["fix_guide"]["windows_fix_guide"]],
        "",
        "## Safety Boundary",
        "",
        "- Current stage is local run doctor only.",
        "- It does not automatically install dependencies.",
        "- It does not connect to a real broker.",
        "- It does not connect to a sandbox API.",
        "- It does not read secrets.",
        "- It does not read accounts, balances, or positions.",
        "- It does not submit orders.",
        "- It does not connect to real money.",
        "",
        "## Missing Local Requirements",
        "",
        "- Start commands remain manual copy/paste steps.",
        "- Browser opening remains a local user action.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"report_generated": True, "path": "reports/v5_42_local_run_doctor_report.md", **boundary()}


def summarize_local_run_doctor_report(result: dict) -> dict:
    return {"report_generated": result.get("report_generated", False), "path": result.get("path", ""), "warnings": result.get("warnings", []), "errors": result.get("errors", []), **boundary()}

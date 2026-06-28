from __future__ import annotations

from pathlib import Path

from config.v5_sandbox_simulation_config import get_sandbox_simulation_status
from sandbox_sim.sandbox_simulation_faults import list_sandbox_faults
from sandbox_sim.sandbox_simulation_runner import run_sandbox_simulation_session


REPORT_PATH = Path("reports/v5_11_sandbox_simulation_harness_report.md")


def build_sandbox_simulation_summary(scenario: str = "full_fill", max_ticks: int = 100) -> dict:
    status = get_sandbox_simulation_status()
    run = run_sandbox_simulation_session(scenario=scenario, max_ticks=max_ticks)
    verdict = "PASS" if run["success"] and not run["errors"] and scenario == "full_fill" else "WARNING"
    return {
        "version": "V5.11",
        "verdict": verdict,
        "status": status,
        "summary": run,
        "simulated_faults": list_sandbox_faults(),
        "manual_approval_simulated": True,
        "safety_boundary": {
            "local_simulation_only": True,
            "real_sandbox_api_enabled": False,
            "broker_connected": False,
            "real_orders_enabled": False,
            "real_money_enabled": False,
            "production_live_trading": False,
        },
        "missing_production_requirements": [
            "external sandbox connector remains disabled",
            "credential vault remains unconfigured",
            "production live trading remains out of scope",
        ],
    }


def generate_sandbox_simulation_report(scenario: str = "full_fill", max_ticks: int = 100) -> dict:
    payload = build_sandbox_simulation_summary(scenario=scenario, max_ticks=max_ticks)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary = payload["summary"]
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# V5.11 Sandbox Simulation Harness Report",
                "",
                f"Final verdict: {payload['verdict']}",
                "",
                "This report covers local sandbox simulation only.",
                "",
                "Safety boundary:",
                "",
                "- Local sandbox simulation only: yes",
                "- Sandbox API connection: no",
                "- Real broker connection: no",
                "- Real order submission: no",
                "- Real capital movement: no",
                "- Production live trading: no",
                "",
                "Simulation summary:",
                "",
                f"- Scenario: {summary['scenario']}",
                f"- Ticks processed: {summary['ticks_processed']}",
                f"- Signals generated: {summary['signals_generated']}",
                f"- Approval requests simulated: {summary['approval_requests']}",
                f"- Simulated orders: {summary['simulated_orders']}",
                f"- Simulated fills: {summary['simulated_fills']}",
                f"- Simulated rejects: {summary['simulated_rejects']}",
                f"- Simulated cancels: {summary['simulated_cancels']}",
                f"- Final equity: {summary['final_equity']}",
                "",
                "Missing production requirements:",
                "",
                "- External sandbox connector remains disabled.",
                "- Credential vault remains unconfigured.",
                "- Production live trading remains out of scope.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {"path": REPORT_PATH.as_posix(), "verdict": payload["verdict"], "summary": summary, "simulation_only": True}

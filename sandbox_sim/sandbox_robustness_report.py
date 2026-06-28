from __future__ import annotations

from pathlib import Path

from config.v5_sandbox_robustness_config import get_sandbox_robustness_status
from sandbox_sim.fault_combination_runner import run_all_fault_combinations
from sandbox_sim.long_run_robustness_runner import run_long_run_robustness, summarize_long_run_robustness
from sandbox_sim.multi_symbol_simulator import run_multi_symbol_simulation, summarize_multi_symbol_result
from sandbox_sim.robustness_consistency_validator import validate_robustness_result
from sandbox_sim.robustness_scenario_matrix import build_robustness_scenario_matrix


REPORT_PATH = Path("reports/v5_12_sandbox_simulation_robustness_report.md")


def build_sandbox_robustness_summary(scenario: str = "full_fill", ticks: int = 1000, all_scenarios: bool = False) -> dict:
    status = get_sandbox_robustness_status()
    scenarios = status["scenarios"] if all_scenarios else [scenario]
    multi = run_multi_symbol_simulation(status["symbols"], scenario=scenario, ticks=min(ticks, 1000), seed=42)
    validation = validate_robustness_result(multi)
    faults = run_all_fault_combinations(ticks=min(ticks, 100), seed=42)
    long_run = run_long_run_robustness(ticks=ticks, symbols=status["symbols"], scenarios=scenarios, seed=42)
    verdict = long_run["final_verdict"] if validation["valid"] else "FAIL"
    return {
        "version": "V5.12",
        "verdict": verdict,
        "status": status,
        "scenario_matrix": build_robustness_scenario_matrix(),
        "multi_symbol_result": multi,
        "multi_symbol_summary": summarize_multi_symbol_result(multi),
        "fault_combination_result": faults,
        "long_run_robustness": long_run,
        "long_run_summary": summarize_long_run_robustness(long_run),
        "consistency_validation": validation,
        "safety_boundary": {
            "local_robustness_only": True,
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
        "simulation_only": True,
    }


def generate_sandbox_robustness_report(scenario: str = "full_fill", ticks: int = 1000, all_scenarios: bool = False) -> dict:
    payload = build_sandbox_robustness_summary(scenario=scenario, ticks=ticks, all_scenarios=all_scenarios)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    long_run = payload["long_run_robustness"]
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# V5.12 Sandbox Simulation Robustness Report",
                "",
                f"Final verdict: {payload['verdict']}",
                "",
                "Current mode is local sandbox simulation robustness only.",
                "",
                "Safety boundary:",
                "",
                "- Sandbox API connection: no",
                "- Real broker connection: no",
                "- Real order submission: no",
                "- Real capital movement: no",
                "- Production live trading: no",
                "",
                "Robustness summary:",
                "",
                f"- Robustness mode: {payload['status']['sandbox_robustness_mode']}",
                f"- Scenario matrix count: {len(payload['scenario_matrix']['scenarios'])}",
                f"- Symbols: {', '.join(payload['status']['symbols'])}",
                f"- Ticks processed: {long_run['ticks_processed']}",
                f"- Pass count: {long_run['pass_count']}",
                f"- Warning count: {long_run['warning_count']}",
                f"- Fail count: {long_run['fail_count']}",
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
    return {"path": REPORT_PATH.as_posix(), "verdict": payload["verdict"], "summary": payload, "simulation_only": True}

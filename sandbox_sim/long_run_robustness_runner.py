from __future__ import annotations

from config.v5_sandbox_robustness_config import DEFAULT_SCENARIOS, DEFAULT_SYMBOLS
from sandbox_sim.multi_symbol_simulator import run_multi_symbol_simulation
from sandbox_sim.robustness_consistency_validator import validate_robustness_result


def run_long_run_robustness(
    ticks: int = 1000,
    symbols: list[str] | None = None,
    scenarios: list[str] | None = None,
    seed: int = 42,
) -> dict:
    selected_symbols = symbols or DEFAULT_SYMBOLS
    selected_scenarios = scenarios or DEFAULT_SCENARIOS
    results = []
    pass_count = warning_count = fail_count = 0
    for index, scenario in enumerate(selected_scenarios):
        run = run_multi_symbol_simulation(selected_symbols, scenario=scenario, ticks=ticks, seed=seed + index)
        validation = validate_robustness_result(run)
        if not validation["valid"]:
            verdict = "FAIL"
            fail_count += 1
        elif scenario in {"full_fill"}:
            verdict = "PASS"
            pass_count += 1
        else:
            verdict = "WARNING"
            warning_count += 1
        results.append({"scenario": scenario, "verdict": verdict, "validation": validation, "result": run})
    final = "FAIL" if fail_count else ("WARNING" if warning_count else "PASS")
    return {
        "ticks_processed": ticks,
        "symbols": selected_symbols,
        "scenarios": selected_scenarios,
        "scenario_results": results,
        "pass_count": pass_count,
        "warning_count": warning_count,
        "fail_count": fail_count,
        "final_verdict": final,
        "simulation_only": True,
        "broker_connected": False,
        "real_order_submitted": False,
        "real_money_enabled": False,
        "real_orders_enabled": False,
        "paper_trading": True,
    }


def summarize_long_run_robustness(result: dict) -> dict:
    return {
        "ticks_processed": result.get("ticks_processed", 0),
        "scenario_count": len(result.get("scenario_results", [])),
        "pass_count": result.get("pass_count", 0),
        "warning_count": result.get("warning_count", 0),
        "fail_count": result.get("fail_count", 0),
        "final_verdict": result.get("final_verdict", "FAIL"),
        "simulation_only": True,
    }

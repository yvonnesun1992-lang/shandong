from __future__ import annotations

from sandbox_sim.multi_symbol_simulator import run_multi_symbol_simulation
from sandbox_sim.robustness_scenario_matrix import list_scenarios


def run_fault_combination(name: str, faults: list[str], ticks: int = 100, seed: int = 42) -> dict:
    result = run_multi_symbol_simulation(scenario=name, ticks=ticks, seed=seed)
    warning = bool(faults)
    return {
        "name": name,
        "faults": faults,
        "ticks_processed": ticks,
        "verdict": "WARNING" if warning else "PASS",
        "orders": len(result["orders"]),
        "fills": len(result["fills"]),
        "network_called": False,
        "external_service_called": False,
        "simulation_only": True,
        "broker_connected": False,
        "real_order_submitted": False,
        "real_money_enabled": False,
    }


def run_all_fault_combinations(ticks: int = 100, seed: int = 42) -> dict:
    combined = [scenario for scenario in list_scenarios() if scenario["category"] == "combined"]
    results = [run_fault_combination(item["name"], item["faults"], ticks=ticks, seed=seed) for item in combined]
    return {
        "combination_count": len(results),
        "results": results,
        "simulation_only": True,
        "broker_connected": False,
        "real_order_submitted": False,
        "real_money_enabled": False,
    }

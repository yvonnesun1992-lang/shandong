from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


SENSITIVE_TERMS = [
    "secret",
    "token",
    "password",
    "api_key",
    "authorization",
    "broker credential",
    "account_id",
    "real_order_id",
    "/users/apple",
]


def test_sandbox_robustness_config_defaults_are_local_only():
    from config.v5_sandbox_robustness_config import get_sandbox_robustness_status

    status = get_sandbox_robustness_status()

    assert status["sandbox_robustness_mode"] == "local_robustness"
    assert status["local_robustness"] is True
    assert status["real_sandbox_api_enabled"] is False
    assert status["broker_connected"] is False
    assert status["real_orders_enabled"] is False
    assert status["real_money_enabled"] is False
    assert status["paper_trading"] is True
    assert status["simulation_only"] is True
    assert {"AAPL", "MSFT", "NVDA", "SPY", "QQQ"}.issubset(set(status["symbols"]))
    assert _is_safe(status)


def test_scenario_matrix_contains_base_and_combined_scenarios():
    from sandbox_sim.robustness_scenario_matrix import build_robustness_scenario_matrix, get_scenario_by_name

    matrix = build_robustness_scenario_matrix()
    names = {item["name"] for item in matrix["scenarios"]}

    assert {"full_fill", "partial_fill", "reject", "cancel", "latency", "disconnect", "insufficient_cash", "invalid_symbol", "risk_rejected"}.issubset(names)
    assert {"latency_partial_fill", "disconnect_missing_fill_report", "partial_fill_stuck_manual_reject"}.issubset(names)
    assert get_scenario_by_name("latency_partial_fill")["category"] == "combined"
    assert all(item["simulation_only"] is True for item in matrix["scenarios"])
    assert _is_safe(matrix)


def test_multi_symbol_simulation_covers_default_symbols_and_lifecycles():
    from sandbox_sim.multi_symbol_simulator import run_multi_symbol_simulation, summarize_multi_symbol_result

    result = run_multi_symbol_simulation(["AAPL", "MSFT", "NVDA", "SPY", "QQQ"], scenario="partial_fill", ticks=20, seed=7)
    summary = summarize_multi_symbol_result(result)

    assert result["ticks_processed"] == 20
    assert set(result["symbols"]) == {"AAPL", "MSFT", "NVDA", "SPY", "QQQ"}
    assert all(result["orders_by_symbol"][symbol] >= 1 for symbol in result["symbols"])
    assert all(result["lifecycle_by_symbol"][symbol] for symbol in result["symbols"])
    assert summary["total_orders"] >= 5
    assert result["simulation_only"] is True
    assert result["broker_connected"] is False
    assert result["real_order_submitted"] is False
    assert result["real_money_enabled"] is False
    assert _is_safe(result)


def test_fault_combination_runner_is_local_only():
    from sandbox_sim.fault_combination_runner import run_all_fault_combinations, run_fault_combination

    one = run_fault_combination("latency_partial_fill", ["network_latency", "partial_fill_stuck"], ticks=10, seed=1)
    all_results = run_all_fault_combinations(ticks=10, seed=1)

    assert one["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert one["network_called"] is False
    assert one["broker_connected"] is False
    assert all_results["combination_count"] >= 7
    assert all(item["simulation_only"] is True for item in all_results["results"])
    assert _is_safe({"one": one, "all": all_results})


def test_consistency_validator_accepts_valid_results_and_blocks_leakage():
    from sandbox_sim.multi_symbol_simulator import run_multi_symbol_simulation
    from sandbox_sim.robustness_consistency_validator import validate_robustness_result

    full = run_multi_symbol_simulation(["AAPL", "MSFT"], scenario="full_fill", ticks=5, seed=2)
    rejected = run_multi_symbol_simulation(["AAPL"], scenario="reject", ticks=5, seed=2)
    leaked = {**full, "note": "token=abc123"}

    assert validate_robustness_result(full)["valid"] is True
    assert validate_robustness_result(rejected)["valid"] is True
    assert validate_robustness_result(leaked)["valid"] is False


def test_long_run_robustness_runner_handles_1000_ticks():
    from sandbox_sim.long_run_robustness_runner import run_long_run_robustness, summarize_long_run_robustness

    result = run_long_run_robustness(ticks=1000, symbols=["AAPL", "MSFT"], scenarios=["full_fill", "reject"], seed=3)
    summary = summarize_long_run_robustness(result)

    assert result["ticks_processed"] == 1000
    assert result["final_verdict"] in {"PASS", "WARNING", "FAIL"}
    assert result["pass_count"] + result["warning_count"] + result["fail_count"] == len(result["scenario_results"])
    assert summary["final_verdict"] == result["final_verdict"]
    assert result["simulation_only"] is True
    assert result["broker_connected"] is False
    assert result["real_order_submitted"] is False
    assert result["real_money_enabled"] is False
    assert _is_safe(result)


def test_sandbox_robustness_report_and_cli_can_run():
    from sandbox_sim.sandbox_robustness_report import generate_sandbox_robustness_report

    report = generate_sandbox_robustness_report(scenario="full_fill", ticks=20)
    assert report["path"].endswith("reports/v5_12_sandbox_simulation_robustness_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(report)

    commands = [
        [sys.executable, "scripts/run_v512_sandbox_robustness.py", "--scenario", "full_fill", "--ticks", "20"],
        [sys.executable, "scripts/run_v512_sandbox_robustness.py", "--all-scenarios", "--ticks", "20"],
    ]
    for command in commands:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
        assert payload["simulation_only"] is True
        assert _is_safe(payload)


def test_sandbox_robustness_api_endpoints_are_safe():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/sandbox-robustness/status",
        "/api/v5/sandbox-robustness/scenario-matrix",
        "/api/v5/sandbox-robustness/multi-symbol",
        "/api/v5/sandbox-robustness/fault-combinations",
        "/api/v5/sandbox-robustness/long-run",
        "/api/v5/sandbox-robustness/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "simulation_only" in encoded
        assert "real_sandbox_api_enabled" in encoded
        assert "broker_connected" in encoded
        assert "real_orders_enabled" in encoded
        assert "real_money_enabled" in encoded
        assert "paper_trading" in encoded
        assert _is_safe(payload)


def test_frontend_docs_review_and_security_scan_include_v512():
    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-sandbox-robustness/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5SandboxRobustnessStatus" in api_client
    assert "fetchV5SandboxRobustnessScenarioMatrix" in api_client
    assert "fetchV5SandboxRobustnessMultiSymbol" in api_client
    assert "fetchV5SandboxRobustnessFaultCombinations" in api_client
    assert "fetchV5SandboxRobustnessLongRun" in api_client
    assert "fetchV5SandboxRobustnessSummary" in api_client
    assert "Sandbox Robustness Status" in page
    assert "Local robustness simulation only" in page
    assert "Sandbox API: disabled" in page
    assert "Broker connected: false" in page
    assert "Real orders: disabled" in page
    assert "Real money: disabled" in page
    assert "Paper trading only" in page
    assert "V5 Sandbox Robustness" in shell
    assert "/v5-sandbox-robustness" in shell
    assert "V5.12" in _read("docs/V5_SANDBOX_SIMULATION_ROBUSTNESS.md")
    assert "V5.12" in _read("README.md")
    assert "V5.12" in _read("REVIEW_PACKAGE.md")
    assert "scan_sandbox_robustness_outputs" in _read("runtime/security_scan.py")
    assert _is_safe(page)


def test_existing_v5_stack_tests_are_available_through_v511():
    required_tests = [
        "tests/test_v50_paper_trading_core.py",
        "tests/test_v51_trading_engine_runtime.py",
        "tests/test_v52_production_stability_engineering.py",
        "tests/test_v53_long_run_soak_test.py",
        "tests/test_v54_live_paper_trading_monitoring_api.py",
        "tests/test_v55_production_deployment_dry_run.py",
        "tests/test_v56_live_paper_trading_staging.py",
        "tests/test_v57_live_alpha_signal_integration.py",
        "tests/test_v58_broker_integration_planning.py",
        "tests/test_v59_manual_approval_gate.py",
        "tests/test_v510_broker_sandbox_readiness.py",
        "tests/test_v511_sandbox_simulation_harness.py",
    ]
    for path in required_tests:
        assert Path(path).exists()


def test_no_real_broker_sdk_network_or_live_order_routing_is_introduced():
    planned_files = [
        "config/v5_sandbox_robustness_config.py",
        "sandbox_sim/robustness_scenario_matrix.py",
        "sandbox_sim/multi_symbol_simulator.py",
        "sandbox_sim/fault_combination_runner.py",
        "sandbox_sim/robustness_consistency_validator.py",
        "sandbox_sim/long_run_robustness_runner.py",
        "sandbox_sim/sandbox_robustness_report.py",
    ]
    forbidden = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "place_order",
        "live_order",
        "sandbox.submit",
        "requests.",
        "httpx.",
    ]
    for path in planned_files:
        text = _read(path).lower()
        assert not any(term in text for term in forbidden)


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _is_safe(payload: object) -> bool:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    allowed = [
        "no secret",
        "no secrets",
        "no broker key",
        "secret / token / password",
        "authorization",
    ]
    for item in allowed:
        text = text.replace(item, "")
    return not any(term in text for term in SENSITIVE_TERMS)

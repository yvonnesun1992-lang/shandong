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


def test_sandbox_simulation_config_defaults_are_local_only():
    from config.v5_sandbox_simulation_config import get_sandbox_simulation_status

    status = get_sandbox_simulation_status()

    assert status["sandbox_simulation_mode"] == "local_simulation"
    assert status["local_simulation"] is True
    assert status["local_sandbox_simulation_enabled"] is True
    assert status["real_sandbox_api_enabled"] is False
    assert status["real_broker_enabled"] is False
    assert status["broker_connected"] is False
    assert status["real_orders_enabled"] is False
    assert status["real_money_enabled"] is False
    assert status["paper_trading"] is True
    assert status["simulation_only"] is True
    assert _is_safe(status)


def test_simulated_account_tracks_cash_positions_and_equity_locally():
    from sandbox_sim.simulated_sandbox_account import SimulatedSandboxAccount
    from sandbox_sim.simulated_sandbox_order import SimulatedSandboxFill

    account = SimulatedSandboxAccount(initial_cash=1000)
    fill = SimulatedSandboxFill.create("SIM-1", "AAPL", "BUY", 2, 100, commission=1)

    account.apply_fill(fill)
    account.update_market_price("AAPL", 110)
    snapshot = account.get_account_snapshot()
    positions = account.get_positions_snapshot()

    assert snapshot["cash"] == 799
    assert snapshot["positions"]["AAPL"] == 2
    assert snapshot["equity"] == 1019
    assert snapshot["buying_power"] == 799
    assert snapshot["broker_connected"] is False
    assert positions[0]["symbol"] == "AAPL"
    assert positions[0]["quantity"] == 2
    assert _is_safe(snapshot)


def test_simulated_order_and_fill_do_not_expose_real_broker_fields():
    from sandbox_sim.simulated_sandbox_order import SimulatedSandboxOrder

    order = SimulatedSandboxOrder.create(symbol="AAPL", side="BUY", quantity=5, order_type="MARKET")
    payload = order.to_dict()

    assert payload["sandbox_order_id"].startswith("SIM-")
    assert payload["simulation_only"] is True
    assert payload["status"] == "NEW"
    assert "broker_order_id" not in payload
    assert "account_id" not in payload
    assert "routing" not in payload
    assert _is_safe(payload)


def test_simulation_broker_full_partial_reject_and_cancel_scenarios():
    from sandbox_sim.sandbox_simulation_broker import SandboxSimulationBroker

    full = SandboxSimulationBroker(scenario="full_fill")
    full_order = full.submit_order({"symbol": "AAPL", "side": "BUY", "quantity": 4})
    full.step_market({"symbol": "AAPL", "price": 100, "timestamp": "2026-01-01T09:31:00Z"})
    assert full.get_order_status(full_order["sandbox_order_id"])["status"] == "FILLED"
    assert len(full.get_recent_fills()) == 1
    assert full.get_recent_orders()[0]["real_order_submitted"] is False

    partial = SandboxSimulationBroker(scenario="partial_fill")
    partial_order = partial.submit_order({"symbol": "MSFT", "side": "BUY", "quantity": 5})
    partial.step_market({"symbol": "MSFT", "price": 50, "timestamp": "2026-01-01T09:32:00Z"})
    assert partial.get_order_status(partial_order["sandbox_order_id"])["status"] == "PARTIALLY_FILLED"
    assert partial.get_recent_fills()[0]["quantity"] == 2

    reject = SandboxSimulationBroker(scenario="reject")
    rejected_order = reject.submit_order({"symbol": "TSLA", "side": "BUY", "quantity": 1})
    reject.step_market({"symbol": "TSLA", "price": 200})
    assert reject.get_order_status(rejected_order["sandbox_order_id"])["status"] == "REJECTED"

    cancel = SandboxSimulationBroker(scenario="latency")
    cancel_order = cancel.submit_order({"symbol": "NVDA", "side": "BUY", "quantity": 1})
    canceled = cancel.cancel_order(cancel_order["sandbox_order_id"])
    assert canceled["status"] == "CANCELED"
    assert _is_safe({"full": full.get_recent_orders(), "fills": full.get_recent_fills()})


def test_lifecycle_simulator_blocks_real_broker_states():
    from sandbox_sim.order_lifecycle_simulator import OrderLifecycleSimulator
    from sandbox_sim.simulated_sandbox_order import SimulatedSandboxOrder

    simulator = OrderLifecycleSimulator()
    order = SimulatedSandboxOrder.create(symbol="AAPL", side="BUY", quantity=1, order_type="MARKET")

    assert simulator.transition(order, "ACCEPTED")["accepted"] is True
    assert simulator.transition(order, "LIVE_SUBMITTED")["accepted"] is False
    assert simulator.transition(order, "REAL_ORDER_READY")["accepted"] is False
    assert simulator.transition(order, "BROKER_ACCEPTED_REAL")["accepted"] is False
    assert order.status == "ACCEPTED"


def test_faults_are_local_and_do_not_call_network_or_broker():
    from sandbox_sim.sandbox_simulation_faults import build_sandbox_fault

    fault = build_sandbox_fault("broker_disconnect")

    assert fault["fault"] == "broker_disconnect"
    assert fault["active"] is True
    assert fault["simulation_only"] is True
    assert fault["broker_connected"] is False
    assert fault["real_order_submitted"] is False
    assert _is_safe(fault)


def test_sandbox_simulation_runner_and_report_cli():
    from sandbox_sim.sandbox_simulation_report import generate_sandbox_simulation_report
    from sandbox_sim.sandbox_simulation_runner import run_sandbox_simulation_session

    result = run_sandbox_simulation_session(scenario="full_fill", max_ticks=5)
    assert result["success"] is True
    assert result["scenario"] == "full_fill"
    assert result["ticks_processed"] == 5
    assert result["simulated_orders"] >= 1
    assert result["simulated_fills"] >= 1
    assert result["simulation_only"] is True
    assert result["broker_connected"] is False
    assert result["real_order_submitted"] is False
    assert result["real_money_enabled"] is False

    report = generate_sandbox_simulation_report("reject", max_ticks=3)
    assert report["path"].endswith("reports/v5_11_sandbox_simulation_harness_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(result)
    assert _is_safe(report)

    for scenario in ["full_fill", "reject"]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v511_sandbox_simulation.py", "--scenario", scenario, "--ticks", "5"],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["summary"]["scenario"] == scenario
        assert payload["summary"]["simulation_only"] is True
        assert _is_safe(payload)


def test_sandbox_simulation_api_endpoints_are_safe():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/sandbox-sim/status",
        "/api/v5/sandbox-sim/account",
        "/api/v5/sandbox-sim/orders",
        "/api/v5/sandbox-sim/fills",
        "/api/v5/sandbox-sim/scenarios",
        "/api/v5/sandbox-sim/summary",
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


def test_frontend_docs_review_and_security_scan_include_v511():
    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-sandbox-sim/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5SandboxSimStatus" in api_client
    assert "fetchV5SandboxSimAccount" in api_client
    assert "fetchV5SandboxSimOrders" in api_client
    assert "fetchV5SandboxSimFills" in api_client
    assert "fetchV5SandboxSimScenarios" in api_client
    assert "fetchV5SandboxSimSummary" in api_client
    assert "Sandbox Simulation Status" in page
    assert "Local simulation only" in page
    assert "Sandbox API: disabled" in page
    assert "Broker connected: false" in page
    assert "Real orders: disabled" in page
    assert "Real money: disabled" in page
    assert "Paper trading only" in page
    assert "V5 Sandbox Sim" in shell
    assert "/v5-sandbox-sim" in shell
    assert "V5.11" in _read("docs/V5_SANDBOX_SIMULATION_HARNESS.md")
    assert "V5.11" in _read("README.md")
    assert "V5.11" in _read("REVIEW_PACKAGE.md")
    assert "scan_sandbox_simulation_outputs" in _read("runtime/security_scan.py")
    assert _is_safe(page)


def test_existing_v5_stack_tests_are_available_through_v510():
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
    ]
    for path in required_tests:
        assert Path(path).exists()


def test_no_real_broker_sdk_or_live_order_routing_is_introduced():
    planned_files = [
        "config/v5_sandbox_simulation_config.py",
        "sandbox_sim/simulated_sandbox_account.py",
        "sandbox_sim/simulated_sandbox_order.py",
        "sandbox_sim/sandbox_simulation_broker.py",
        "sandbox_sim/order_lifecycle_simulator.py",
        "sandbox_sim/sandbox_simulation_faults.py",
        "sandbox_sim/sandbox_simulation_runner.py",
        "sandbox_sim/sandbox_simulation_report.py",
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
    allowed_policy_fields = [
        "plaintext_secret_allowed",
        "frontend_secret_exposure_allowed",
        "no secret",
        "no secrets",
        "no broker key",
        "secret / token / password",
        "authorization",
    ]
    for allowed in allowed_policy_fields:
        text = text.replace(allowed, "")
    return not any(term in text for term in SENSITIVE_TERMS)

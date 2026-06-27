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
    "/users/apple",
]


def test_broker_integration_config_defaults_are_planning_only():
    from config.v5_broker_integration_config import get_broker_integration_status

    status = get_broker_integration_status()

    assert status["broker_integration_mode"] == "disabled"
    assert status["broker_provider"] == "none"
    assert status["broker_execution_mode"] == "paper_only"
    assert status["enable_broker"] is False
    assert status["broker_connected"] is False
    assert status["real_orders_enabled"] is False
    assert status["real_money_enabled"] is False
    assert status["paper_trading"] is True
    assert _is_safe(status)


def test_broker_adapter_interface_is_planned_only():
    from broker.broker_adapter_interface import BrokerAdapterInterface

    adapter = BrokerAdapterInterface()

    for method_name, args in [
        ("get_account", ()),
        ("get_positions", ()),
        ("submit_order", ({"symbol": "AAPL", "side": "BUY"},)),
        ("cancel_order", ("planned-order",)),
        ("get_order_status", ("planned-order",)),
    ]:
        method = getattr(adapter, method_name)
        try:
            method(*args)
        except NotImplementedError as exc:
            assert "planned" in str(exc).lower() or "not implemented" in str(exc).lower()
        else:
            raise AssertionError(f"{method_name} must not connect to a broker")


def test_planned_broker_adapter_rejects_all_real_order_attempts():
    from broker.planned_broker_adapter import PlannedBrokerAdapter

    adapter = PlannedBrokerAdapter(provider="alpaca_planned")

    account = adapter.get_account()
    positions = adapter.get_positions()
    submitted = adapter.submit_order({"symbol": "AAPL", "side": "BUY", "quantity": 1})
    cancelled = adapter.cancel_order("planned-order")
    status = adapter.get_order_status("planned-order")

    assert account["broker_connected"] is False
    assert positions == []
    for payload in [submitted, cancelled, status]:
        assert payload["status"] in {"rejected", "planned_only"}
        assert payload["real_order_submitted"] is False
        assert payload["paper_trading"] is True
        assert "planned only" in payload["reason"]
        assert _is_safe(payload)


def test_broker_safety_gate_rejects_real_order_attempts():
    from broker.broker_safety_gate import broker_readiness_summary, reject_real_order_attempt, validate_broker_safety

    safety = validate_broker_safety()
    rejected = reject_real_order_attempt({"symbol": "AAPL", "side": "BUY", "quantity": 1})
    summary = broker_readiness_summary()

    assert safety["safe"] is True
    assert safety["broker_connected"] is False
    assert safety["real_orders_enabled"] is False
    assert safety["real_money_enabled"] is False
    assert rejected["status"] == "rejected"
    assert rejected["real_order_submitted"] is False
    assert summary["readiness"] in {"planning_only", "not_ready_for_live_broker"}
    assert _is_safe({"safety": safety, "rejected": rejected, "summary": summary})


def test_order_mapping_plan_does_not_generate_real_broker_order():
    from broker.order_mapping_plan import build_order_mapping_plan, map_paper_order_to_broker_plan

    plan = build_order_mapping_plan()
    mapped = map_paper_order_to_broker_plan({"symbol": "AAPL", "side": "BUY", "quantity": 10, "order_type": "MARKET"})

    assert plan["mapping_ready"] is False
    assert "symbol" in plan["planned_fields"]
    assert "broker_account_reference" in plan["unsupported_fields"]
    assert mapped["mapping_ready"] is False
    assert mapped["real_broker_order"] is None
    assert mapped["real_order_generated"] is False
    assert _is_safe({"plan": plan, "mapped": mapped})


def test_broker_api_endpoints_return_safe_planning_payloads():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())

    for path in ["/api/v5/broker/status", "/api/v5/broker/readiness", "/api/v5/broker/safety", "/api/v5/broker/order-mapping"]:
        response = client.get(path)
        payload = response.json()

        assert response.status_code == 200
        assert payload["success"] is True
        encoded = json.dumps(payload).lower()
        assert "broker_connected" in encoded
        assert "real_orders_enabled" in encoded
        assert "real_money_enabled" in encoded
        assert "paper_trading" in encoded
        assert _is_safe(payload)


def test_broker_integration_report_and_cli_can_run():
    from broker.broker_integration_report import generate_broker_integration_report

    result = generate_broker_integration_report()
    assert result["path"].endswith("reports/v5_8_broker_integration_planning_report.md")
    assert result["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(result)

    completed = subprocess.run(
        [sys.executable, "scripts/run_v58_broker_integration_planning.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode in {0, 1}
    payload = json.loads(completed.stdout)
    assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(payload)


def test_v58_frontend_helpers_navigation_docs_and_review_exist():
    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-broker/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5BrokerStatus" in api_client
    assert "fetchV5BrokerReadiness" in api_client
    assert "fetchV5BrokerSafety" in api_client
    assert "fetchV5BrokerOrderMapping" in api_client
    assert "Broker Integration Status" in page
    assert "Broker connected: false" in page
    assert "Real orders: disabled" in page
    assert "Real money: disabled" in page
    assert "Paper trading only" in page
    assert "Planning only" in page
    assert "V5 Broker" in shell
    assert "/v5-broker" in shell
    assert "V5.8" in _read("docs/V5_BROKER_INTEGRATION_PLANNING.md")
    assert "V5.8" in _read("README.md")
    assert "V5.8" in _read("REVIEW_PACKAGE.md")
    assert _is_safe(page)


def test_existing_v5_stack_tests_are_available():
    assert "test_paper_trading_runner_completes_closed_loop" in _read("tests/test_v50_paper_trading_core.py")
    assert "test_runtime_loop_runs_and_updates_portfolio" in _read("tests/test_v51_trading_engine_runtime.py")
    assert "test_engine_crash_recovery_logs_error" in _read("tests/test_v52_production_stability_engineering.py")
    assert "soak" in _read("tests/test_v53_long_run_soak_test.py").lower()
    assert "monitoring" in _read("tests/test_v54_live_paper_trading_monitoring_api.py").lower()
    assert "deployment" in _read("tests/test_v55_production_deployment_dry_run.py").lower()
    assert "live paper" in _read("tests/test_v56_live_paper_trading_staging.py").lower()
    assert "live alpha" in _read("tests/test_v57_live_alpha_signal_integration.py").lower()


def test_no_real_broker_sdk_or_order_routing_is_introduced():
    planned_files = [
        "config/v5_broker_integration_config.py",
        "broker/broker_adapter_interface.py",
        "broker/planned_broker_adapter.py",
        "broker/order_mapping_plan.py",
        "broker/broker_safety_gate.py",
        "broker/broker_integration_report.py",
    ]
    forbidden = ["alpaca_trade_api", "ib_insync", "tigeropen", "robin_stocks", "place_order", "live_order"]
    for path in planned_files:
        text = _read(path).lower()
        assert not any(term in text for term in forbidden)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _is_safe(payload) -> bool:
    encoded = json.dumps(payload, default=str).lower()
    return not any(term in encoded for term in SENSITIVE_TERMS)

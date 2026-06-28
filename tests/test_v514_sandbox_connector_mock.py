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
    "raw provider response",
    "/users/apple",
]


def test_mock_connector_config_defaults_are_mock_only():
    from config.v5_sandbox_connector_mock_config import get_mock_connector_status

    status = get_mock_connector_status()

    assert status["mock_connector_mode"] == "mock_enabled"
    assert status["mock_connector_provider"] == "mock"
    assert status["mock_connector_enabled"] is True
    assert status["real_connector_runtime_enabled"] is False
    assert status["real_sandbox_api_enabled"] is False
    assert status["broker_connected"] is False
    assert status["real_orders_enabled"] is False
    assert status["real_money_enabled"] is False
    assert status["paper_trading"] is True
    assert status["mock_only"] is True
    assert _is_safe(status)


def test_mock_connector_account_positions_and_submit_are_sanitized():
    from sandbox_connector.mock_sandbox_connector import MockSandboxConnector
    from sandbox_connector.request_schema_contract import SubmitOrderRequest

    connector = MockSandboxConnector()
    account = connector.get_account()
    positions = connector.get_positions()
    request = SubmitOrderRequest.create("AAPL", "BUY", 3).to_dict()
    response = connector.submit_order(request)

    assert account["sanitized"] is True
    assert positions["sanitized"] is True
    assert response["mock_only"] is True
    assert response["real_order_submitted"] is False
    assert response["broker_connected"] is False
    assert response["provider_order_ref"].startswith(("mock_ref", "planned_ref"))
    assert "broker_order_id" not in response
    assert "account_id" not in response
    assert _is_safe({"account": account, "positions": positions, "response": response})


def test_mock_state_store_does_not_store_sensitive_fields():
    from sandbox_connector.mock_connector_state_store import MockConnectorStateStore

    store = MockConnectorStateStore()
    store.save_order({"client_order_id": "client-1", "note": "secret=abc"})
    store.save_idempotency_key("idem_key", {"note": "token=abc"})

    assert store.get_order("client-1")["note"] == "[redacted]"
    assert store.get_idempotency_response("idem_key")["note"] == "[redacted]"
    assert _is_safe(store.list_orders())


def test_mock_order_lifecycle_blocks_real_states():
    from sandbox_connector.mock_order_lifecycle import build_mock_order_lifecycle_policy, transition_mock_order, validate_mock_order_status

    order = {"status": "MOCK_CREATED"}

    assert transition_mock_order(order, "MOCK_ACCEPTED")["accepted"] is True
    assert validate_mock_order_status("MOCK_FILLED")["valid"] is True
    assert transition_mock_order(order, "LIVE_SUBMITTED")["accepted"] is False
    assert transition_mock_order(order, "REAL_ORDER_READY")["accepted"] is False
    assert build_mock_order_lifecycle_policy()["real_order_path_allowed"] is False


def test_mock_response_factory_uses_mock_refs_and_no_raw_payload():
    from sandbox_connector.mock_response_factory import build_mock_error_response, build_mock_order_response, sanitize_mock_response
    from sandbox_connector.request_schema_contract import SubmitOrderRequest

    request = SubmitOrderRequest.create("MSFT", "BUY", 2).to_dict()
    response = build_mock_order_response(request, "filled")
    error = build_mock_error_response("RATE_LIMITED")
    sanitized = sanitize_mock_response({**response, "raw_provider_response": {"x": "y"}, "note": "password=abc"})

    assert response["provider_order_ref"].startswith("mock_ref")
    assert response["raw_response_available"] is False
    assert response["sanitized"] is True
    assert error["error_code"] == "RATE_LIMITED"
    assert "raw_provider_response" not in sanitized
    assert sanitized["note"] == "[redacted]"
    assert _is_safe(response)


def test_mock_scenario_runner_covers_required_scenarios():
    from sandbox_connector.mock_connector_scenario_runner import run_all_mock_connector_scenarios, run_mock_connector_scenario, summarize_mock_connector_scenarios

    accepted = run_mock_connector_scenario("accepted")
    rate_limited = run_mock_connector_scenario("rate_limited")
    all_results = run_all_mock_connector_scenarios()
    summary = summarize_mock_connector_scenarios(all_results)
    names = {item["scenario"] for item in all_results["results"]}

    assert accepted["status"] in {"PASS", "WARNING", "FAIL"}
    assert rate_limited["scenario"] == "rate_limited"
    assert {"accepted", "rejected", "rate_limited", "timeout"}.issubset(names)
    assert summary["scenario_count"] >= 12
    assert all(item["mock_only"] is True for item in all_results["results"])
    assert _is_safe(all_results)


def test_mock_safety_validator_confirms_no_real_runtime():
    from sandbox_connector.mock_connector_safety_validator import validate_mock_connector_safety, validate_mock_response_safety, validate_no_real_runtime

    safety = validate_mock_connector_safety()
    runtime = validate_no_real_runtime()
    invalid = validate_mock_response_safety({"note": "api_key=abc"})

    assert safety["safe"] is True
    assert runtime["safe"] is True
    assert invalid["safe"] is False
    assert safety["mock_only"] is True
    assert safety["broker_connected"] is False
    assert safety["real_orders_enabled"] is False


def test_sandbox_connector_mock_api_endpoints_are_safe():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/sandbox-connector-mock/status",
        "/api/v5/sandbox-connector-mock/account",
        "/api/v5/sandbox-connector-mock/positions",
        "/api/v5/sandbox-connector-mock/recent-orders",
        "/api/v5/sandbox-connector-mock/scenarios",
        "/api/v5/sandbox-connector-mock/safety",
        "/api/v5/sandbox-connector-mock/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "mock_only" in encoded
        assert "real_connector_runtime_enabled" in encoded
        assert "real_sandbox_api_enabled" in encoded
        assert "broker_connected" in encoded
        assert "real_orders_enabled" in encoded
        assert "real_money_enabled" in encoded
        assert "paper_trading" in encoded
        assert _is_safe(payload)


def test_mock_connector_report_and_cli_can_run():
    from sandbox_connector.mock_connector_report import generate_mock_connector_report

    report = generate_mock_connector_report("accepted")
    assert report["path"].endswith("reports/v5_14_sandbox_connector_mock_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(report)

    for args in [["--scenario", "accepted"], ["--all-scenarios"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v514_sandbox_connector_mock.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
        assert payload["summary"]["mock_only"] is True
        assert _is_safe(payload)


def test_frontend_docs_review_and_security_scan_include_v514():
    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-sandbox-connector-mock/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5SandboxConnectorMockStatus" in api_client
    assert "fetchV5SandboxConnectorMockAccount" in api_client
    assert "fetchV5SandboxConnectorMockPositions" in api_client
    assert "fetchV5SandboxConnectorMockRecentOrders" in api_client
    assert "fetchV5SandboxConnectorMockScenarios" in api_client
    assert "fetchV5SandboxConnectorMockSafety" in api_client
    assert "fetchV5SandboxConnectorMockSummary" in api_client
    assert "Sandbox Connector Mock Status" in page
    assert "Mock connector only" in page
    assert "Connector runtime: disabled" in page
    assert "Sandbox API: disabled" in page
    assert "Broker connected: false" in page
    assert "Real orders: disabled" in page
    assert "Real money: disabled" in page
    assert "Paper trading only" in page
    assert "V5 Sandbox Connector Mock" in shell
    assert "/v5-sandbox-connector-mock" in shell
    assert "V5.14" in _read("docs/V5_SANDBOX_CONNECTOR_MOCK.md")
    assert "V5.14" in _read("README.md")
    assert "V5.14" in _read("REVIEW_PACKAGE.md")
    assert "scan_sandbox_connector_mock_outputs" in _read("runtime/security_scan.py")
    assert _is_safe(page)


def test_existing_v5_stack_tests_are_available_through_v513():
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
        "tests/test_v512_sandbox_simulation_robustness.py",
        "tests/test_v513_sandbox_connector_contract.py",
    ]
    for path in required_tests:
        assert Path(path).exists()


def test_no_real_broker_sdk_network_or_live_order_routing_is_introduced():
    planned_files = [
        "config/v5_sandbox_connector_mock_config.py",
        "sandbox_connector/mock_sandbox_connector.py",
        "sandbox_connector/mock_connector_state_store.py",
        "sandbox_connector/mock_order_lifecycle.py",
        "sandbox_connector/mock_response_factory.py",
        "sandbox_connector/mock_connector_scenario_runner.py",
        "sandbox_connector/mock_connector_safety_validator.py",
        "sandbox_connector/mock_connector_report.py",
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
        "secret / token / password",
        "raw_response_available",
        "raw provider response exposure",
        "authorization",
    ]
    for item in allowed:
        text = text.replace(item, "")
    return not any(term in text for term in SENSITIVE_TERMS)

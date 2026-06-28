from __future__ import annotations

from sandbox_connector.mock_response_factory import SCENARIO_TO_STATUS
from sandbox_connector.mock_sandbox_connector import MockSandboxConnector
from sandbox_connector.request_schema_contract import SubmitOrderRequest


MOCK_SCENARIOS = [
    "accepted",
    "filled",
    "partial_fill",
    "rejected",
    "duplicate",
    "rate_limited",
    "cancel_accepted",
    "cancel_rejected",
    "provider_unavailable",
    "timeout",
    "manual_approval_required",
    "kill_switch_active",
]


def run_mock_connector_scenario(scenario: str = "accepted") -> dict:
    name = scenario if scenario in MOCK_SCENARIOS else "accepted"
    connector = MockSandboxConnector()
    request = SubmitOrderRequest.create("AAPL", "BUY", 3).to_dict()
    request["scenario"] = name
    response = connector.submit_order(request)
    expected_status = SCENARIO_TO_STATUS[name]
    passed = response.get("status") == expected_status and response.get("mock_only") is True
    if name == "duplicate":
        response = connector.submit_order(request)
        passed = response.get("status") == "MOCK_DUPLICATE"
    return {
        "version": "V5.14",
        "scenario": name,
        "status": "PASS" if passed else "FAIL",
        "expected_status": expected_status,
        "response": response,
        "mock_only": True,
        "real_connector_runtime_enabled": False,
        "real_sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": [] if passed else ["mock scenario mismatch"],
    }


def run_all_mock_connector_scenarios() -> dict:
    results = [run_mock_connector_scenario(item) for item in MOCK_SCENARIOS]
    summary = summarize_mock_connector_scenarios({"results": results})
    return {
        "version": "V5.14",
        "results": results,
        "summary": summary,
        "mock_only": True,
        "real_connector_runtime_enabled": False,
        "real_sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def summarize_mock_connector_scenarios(results: dict | list[dict]) -> dict:
    items = results.get("results", []) if isinstance(results, dict) else results
    passed = sum(1 for item in items if item.get("status") == "PASS")
    failed = sum(1 for item in items if item.get("status") == "FAIL")
    return {
        "scenario_count": len(items),
        "passed": passed,
        "failed": failed,
        "verdict": "PASS" if failed == 0 else "FAIL",
        "mock_only": True,
        "broker_connected": False,
        "real_orders_enabled": False,
        "paper_trading": True,
    }

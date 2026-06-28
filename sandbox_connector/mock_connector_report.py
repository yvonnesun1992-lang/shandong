from __future__ import annotations

from pathlib import Path

from config.v5_sandbox_connector_mock_config import get_mock_connector_status
from runtime.security_scan import scan_sandbox_connector_mock_outputs
from sandbox_connector.mock_connector_safety_validator import validate_mock_connector_safety
from sandbox_connector.mock_connector_scenario_runner import run_all_mock_connector_scenarios, run_mock_connector_scenario, summarize_mock_connector_scenarios


REPORT_PATH = Path("reports/v5_14_sandbox_connector_mock_report.md")


def build_mock_connector_summary(scenario: str = "accepted", all_scenarios: bool = False) -> dict:
    status = get_mock_connector_status()
    scenario_result = run_all_mock_connector_scenarios() if all_scenarios else {"results": [run_mock_connector_scenario(scenario)]}
    scenario_summary = scenario_result.get("summary") or summarize_mock_connector_scenarios(scenario_result)
    safety = validate_mock_connector_safety()
    verdict = "PASS" if scenario_summary["verdict"] == "PASS" and safety["safe"] else "FAIL"
    return {
        "version": "V5.14",
        "summary": {
            "mock_only": True,
            "scenario_count": scenario_summary["scenario_count"],
            "passed": scenario_summary["passed"],
            "failed": scenario_summary["failed"],
            "real_connector_runtime_enabled": False,
            "real_sandbox_api_enabled": False,
            "broker_connected": False,
            "real_orders_enabled": False,
            "real_money_enabled": False,
            "paper_trading": True,
        },
        "status": status,
        "scenario_results": scenario_result["results"],
        "safety": safety,
        "verdict": verdict,
        "warnings": [] if verdict == "PASS" else ["mock connector check failed"],
    }


def generate_mock_connector_report(scenario: str = "accepted", all_scenarios: bool = False) -> dict:
    payload = build_mock_connector_summary(scenario=scenario, all_scenarios=all_scenarios)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = _render_report(payload)
    REPORT_PATH.write_text(text, encoding="utf-8")
    scan = scan_sandbox_connector_mock_outputs(payload, REPORT_PATH)
    if not scan["safe"]:
        payload["verdict"] = "FAIL"
        payload.setdefault("warnings", []).append("safety scan found blocked output")
    return {
        "path": REPORT_PATH.as_posix(),
        "verdict": payload["verdict"],
        "summary": payload["summary"],
        "warnings": payload.get("warnings", []),
        "mock_only": True,
        "broker_connected": False,
        "real_orders_enabled": False,
        "paper_trading": True,
    }


def _render_report(payload: dict) -> str:
    summary = payload["summary"]
    return f"""# V5.14 Sandbox Connector Mock Implementation

Verdict: {payload["verdict"]}

## Scope

- Local mock connector implementation only.
- Connector runtime: disabled.
- Sandbox API: disabled.
- Broker connected: false.
- Real orders: disabled.
- Real money: disabled.
- Paper trading only.

## Scenario Summary

- Scenario count: {summary["scenario_count"]}
- Passed: {summary["passed"]}
- Failed: {summary["failed"]}
- Mock connector only: {summary["mock_only"]}

## Safety Boundary

- No real broker connection.
- No sandbox API connection.
- No real account read.
- No real order routing.
- No payment flow.
- No alpha model or factor logic changes.
"""

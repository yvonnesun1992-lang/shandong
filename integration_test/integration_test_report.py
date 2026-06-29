from __future__ import annotations

from pathlib import Path

from integration_test.integration_safety_gate import validate_integration_safety
from integration_test.integration_test_core import IntegrationTestCore
from integration_test.integration_test_orchestrator import run_all_tests, run_scenario, summarize_results
from runtime.security_scan import scan_integration_test_outputs


REPORT_PATH = Path("reports/v5_17_integration_test_harness_report.md")


def build_integration_test_summary(scenario: str = "normal_flow", all_scenarios: bool = False) -> dict:
    core = IntegrationTestCore(seed=42)
    scenario_results = run_all_tests() if all_scenarios else {"results": [run_scenario(scenario)]}
    summary = scenario_results.get("summary") or summarize_results(scenario_results)
    safety = validate_integration_safety({"simulation_only": True})
    full_pipeline = core.run_full_pipeline_test()
    layered = core.run_layered_test()
    failure = core.run_failure_injection_test("connector_timeout")
    verdict = "PASS" if summary["failed"] == 0 and safety["safe"] and full_pipeline["status"] == "PASS" else "FAIL"
    return {
        "version": "V5.17",
        "summary": {
            "integration_only": True,
            "simulation_only": True,
            "total_scenarios": summary["total_scenarios"],
            "passed": summary["passed"],
            "failed": summary["failed"],
            "warnings": summary["warnings"],
            "integration_score": summary["integration_score"],
            "broker_connected": False,
            "real_orders_enabled": False,
        },
        "pipeline": full_pipeline,
        "layers": layered,
        "failure_injection": failure,
        "scenario_results": scenario_results["results"],
        "safety": safety,
        "missing_production_requirements": [
            "real sandbox certification",
            "provider sandbox credentials vault",
            "manual approval operations signoff",
            "external monitoring review",
            "production incident runbook",
        ],
        "verdict": verdict,
        "warnings": [] if verdict == "PASS" else ["integration harness warning"],
    }


def generate_integration_test_report(scenario: str = "normal_flow", all_scenarios: bool = False) -> dict:
    payload = build_integration_test_summary(scenario=scenario, all_scenarios=all_scenarios)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(payload), encoding="utf-8")
    scan = scan_integration_test_outputs(payload, REPORT_PATH)
    if not scan["safe"]:
        payload["verdict"] = "FAIL"
        payload.setdefault("warnings", []).append("safety scan found blocked output")
    return {
        "path": REPORT_PATH.as_posix(),
        "verdict": payload["verdict"],
        "summary": payload["summary"],
        "warnings": payload.get("warnings", []),
        "integration_only": True,
        "broker_connected": False,
        "real_orders_enabled": False,
    }


def _render_report(payload: dict) -> str:
    summary = payload["summary"]
    return f"""# V5.17 Sandbox Connector Integration Test Harness

Verdict: {payload["verdict"]}

## Pipeline Coverage

- Alpha Signal to Paper Trading Engine.
- Manual Approval to Broker Adapter Skeleton.
- Mock Connector to Sandbox Bridge.
- Execution Simulation to Monitoring / Risk / Audit.

## Scenario Matrix Results

- Total scenarios: {summary["total_scenarios"]}
- Passed: {summary["passed"]}
- Failed: {summary["failed"]}
- Integration score: {summary["integration_score"]:.2f}

## Safety Boundary

- Current stage is integration test harness only.
- Current stage does not connect to a real broker.
- Current stage does not connect to sandbox API.
- Current stage does not submit real orders.
- Current stage is not a production system.
"""

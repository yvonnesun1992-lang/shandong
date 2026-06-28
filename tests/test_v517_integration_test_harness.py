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


def test_integration_core_runs_full_pipeline_and_replay():
    from integration_test.integration_test_core import IntegrationTestCore

    core = IntegrationTestCore(seed=42)
    full = core.run_full_pipeline_test()
    layered = core.run_layered_test()
    failure = core.run_failure_injection_test("connector_timeout")
    replay_a = core.run_deterministic_replay_test("normal_flow")
    replay_b = core.run_deterministic_replay_test("normal_flow")

    assert full["status"] in {"PASS", "WARNING"}
    assert full["simulation_only"] is True
    assert full["broker_connected"] is False
    assert full["real_orders_enabled"] is False
    assert layered["status"] in {"PASS", "WARNING"}
    assert failure["failure_injected"] is True
    assert replay_a == replay_b
    assert _is_safe({"full": full, "layered": layered, "failure": failure, "replay": replay_a})


def test_layered_pipeline_tester_and_failure_injection_work():
    from integration_test.failure_injection_engine import FailureInjectionEngine
    from integration_test.layered_pipeline_tester import LayeredPipelineTester

    tester = LayeredPipelineTester(seed=7)
    alpha = tester.test_alpha_layer()
    mock = tester.test_mock_connector_layer()
    skeleton = tester.test_skeleton_adapter_layer()
    bridge = tester.test_bridge_layer()
    e2e = tester.test_end_to_end_flow()
    engine = FailureInjectionEngine(seed=7)
    injected = engine.inject_failure("latency_spike", "bridge")
    scenario = engine.run_with_failure_scenario("full_failure_chain")
    reset = engine.reset_failure_state()

    for result in [alpha, mock, skeleton, bridge, e2e]:
        assert result["simulation_only"] is True
        assert result["broker_connected"] is False
        assert result["network_call_attempted"] is False
        assert result["status"] in {"PASS", "WARNING"}
    assert injected["failure_injected"] is True
    assert scenario["scenario"] == "full_failure_chain"
    assert reset["reset"] is True
    assert _is_safe({"layers": [alpha, mock, skeleton, bridge, e2e], "scenario": scenario})


def test_scenario_matrix_orchestrator_and_consistency_validator():
    from integration_test.cross_layer_consistency_validator import validate_cross_layer_consistency
    from integration_test.integration_scenario_matrix import build_integration_scenario_matrix, replay_scenario
    from integration_test.integration_test_orchestrator import run_all_tests, run_scenario, summarize_results

    matrix = build_integration_scenario_matrix(seed=42)
    normal = replay_scenario("normal_flow", seed=42)
    risk = run_scenario("risk_gate_block_flow")
    all_results = run_all_tests()
    summary = summarize_results(all_results)
    consistency = validate_cross_layer_consistency(normal)

    assert len(matrix["scenarios"]) >= 10
    assert normal["scenario"] == "normal_flow"
    assert risk["scenario"] == "risk_gate_block_flow"
    assert all_results["simulation_only"] is True
    assert summary["total_scenarios"] >= 10
    assert summary["failed"] == 0
    assert summary["integration_score"] >= 0.9
    assert consistency["valid"] is True
    assert consistency["layer_mismatch"] == []
    assert _is_safe({"matrix": matrix, "normal": normal, "summary": summary, "consistency": consistency})


def test_integration_safety_gate_blocks_real_connection_and_sensitive_config():
    from integration_test.integration_safety_gate import validate_integration_safety

    safe = validate_integration_safety({"simulation_only": True})
    real_connection = validate_integration_safety({"real_connection": True})
    network = validate_integration_safety({"network_call_attempted": True})
    sensitive = validate_integration_safety({"credential": "api_key=abc"})

    assert safe["safe"] is True
    assert real_connection["safe"] is False
    assert network["safe"] is False
    assert sensitive["safe"] is False
    assert safe["blocked_real_connection"] is True
    assert safe["reason"] == "V5.17 integration test only"
    assert _is_safe({"safe": safe, "real_connection": real_connection, "network": network})


def test_integration_api_endpoints_return_simulation_flags():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/integration-test/status",
        "/api/v5/integration-test/scenarios",
        "/api/v5/integration-test/run",
        "/api/v5/integration-test/layers",
        "/api/v5/integration-test/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "integration_only" in encoded
        assert "broker_connected" in encoded
        assert "real_orders_enabled" in encoded
        assert "false" in encoded
        assert _is_safe(payload)


def test_report_cli_frontend_docs_and_navigation_are_present():
    from integration_test.integration_test_report import generate_integration_test_report

    report = generate_integration_test_report("normal_flow")
    assert report["path"].endswith("reports/v5_17_integration_test_harness_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["summary"]["integration_only"] is True

    for args in [["--scenario", "normal_flow"], ["--scenario", "full_failure_chain"], ["--all"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v517_integration_test_harness.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
        assert payload["summary"]["integration_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-integration-test/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5IntegrationStatus" in api_client
    assert "fetchV5IntegrationScenarios" in api_client
    assert "fetchV5IntegrationRun" in api_client
    assert "fetchV5IntegrationLayers" in api_client
    assert "fetchV5IntegrationSummary" in api_client
    assert "Integration Pipeline Status" in page
    assert "Layer-by-layer Execution" in page
    assert "Scenario Matrix" in page
    assert "Failure Injection" in page
    assert "Consistency Validation" in page
    assert "Safety Gate Status" in page
    assert "Final Verdict" in page
    assert "simulation only" in page.lower()
    assert "no real broker" in page.lower()
    assert "no sandbox api" in page.lower()
    assert "V5 Integration Test" in shell
    assert "/v5-integration-test" in shell
    assert "V5.17" in _read("docs/V5_INTEGRATION_TEST_HARNESS.md")
    assert "V5.17" in _read("README.md")
    assert "V5.17" in _read("REVIEW_PACKAGE.md")
    assert "scan_integration_test_outputs" in _read("runtime/security_scan.py")
    assert _is_safe(page)


def test_existing_v5_stack_tests_are_available_through_v516():
    for path in [
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
        "tests/test_v514_sandbox_connector_mock.py",
        "tests/test_v515_broker_adapter_skeleton.py",
        "tests/test_v516_sandbox_bridge.py",
    ]:
        assert Path(path).exists()


def test_no_sdk_network_or_real_runtime_strings_in_integration_modules():
    planned_files = [
        "integration_test/integration_test_core.py",
        "integration_test/layered_pipeline_tester.py",
        "integration_test/failure_injection_engine.py",
        "integration_test/cross_layer_consistency_validator.py",
        "integration_test/integration_scenario_matrix.py",
        "integration_test/integration_test_orchestrator.py",
        "integration_test/integration_safety_gate.py",
        "integration_test/integration_test_report.py",
    ]
    forbidden = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "place_order",
        "live_order",
        "requests.",
        "httpx.",
        "oauthlib",
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

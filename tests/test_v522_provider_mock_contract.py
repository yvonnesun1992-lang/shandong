from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}
FALSE_KEYS = [
    "mock_contract_runtime_enabled",
    "sandbox_api_enabled",
    "account_read_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]
PAYLOAD_TYPES = {
    "accepted_order_response",
    "partial_fill_response",
    "filled_order_response",
    "rejected_order_response",
    "canceled_order_response",
    "account_snapshot_placeholder",
    "position_snapshot_placeholder",
    "rate_limit_error",
    "invalid_symbol_error",
    "insufficient_funds_error",
    "market_closed_error",
    "provider_timeout_error",
    "duplicate_order_error",
}


def test_mock_contract_config_defaults_and_blocks_real_path_env(monkeypatch):
    from config.v5_provider_mock_contract_config import get_mock_contract_mode, get_mock_contract_provider, get_mock_contract_status

    assert get_mock_contract_mode() == "mock_contract_only"
    assert get_mock_contract_provider() in PROVIDERS
    status = get_mock_contract_status()
    assert status["mock_contract_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_MOCK_CONTRACT_RUNTIME", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ACCOUNT_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_mock_contract_status()

    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "mock contract runtime requested but blocked in v5.22" in warnings
    assert "sandbox api requested but blocked in v5.22" in warnings
    assert "account read requested but blocked in v5.22" in warnings
    assert "order submission requested but blocked in v5.22" in warnings
    assert "real money requested but blocked in v5.22" in warnings
    assert _is_safe(blocked)


def test_mock_payload_catalog_and_schema_validation_pass():
    from provider_mock_contract.contract_schema_validator import validate_all_mock_payloads, validate_mock_payload_schema
    from provider_mock_contract.mock_provider_payloads import build_all_mock_payloads, build_mock_payload

    payload = build_mock_payload("alpaca", "accepted_order_response")
    payloads = build_all_mock_payloads("alpaca")
    validation = validate_all_mock_payloads("alpaca")

    assert payload["payload_type"] == "accepted_order_response"
    assert payload["provider_order_ref"] == "PROVIDER_ORDER_REF_PLACEHOLDER"
    assert payload["account_ref"] == "ACCOUNT_REF_PLACEHOLDER"
    assert {item["payload_type"] for item in payloads["payloads"]} >= PAYLOAD_TYPES
    assert validate_mock_payload_schema(payload)["valid"] is True
    assert validation["valid"] is True
    assert validation["checked_payloads"] >= len(PAYLOAD_TYPES)
    assert _is_safe(payloads)
    assert _is_safe(validation)


def test_contract_tests_pass_for_request_response_error_idempotency_and_state_machine():
    from provider_mock_contract.error_mapping_contract_test import test_error_mapping
    from provider_mock_contract.idempotency_contract_test import test_idempotency_policy
    from provider_mock_contract.order_state_machine_contract_test import test_order_state_machine
    from provider_mock_contract.request_mapping_contract_test import build_mock_internal_order, test_order_request_mapping
    from provider_mock_contract.response_normalization_contract_test import test_response_normalization

    internal_order = build_mock_internal_order()
    request = test_order_request_mapping("alpaca")
    response = test_response_normalization("alpaca")
    errors = test_error_mapping("alpaca")
    idempotency = test_idempotency_policy("alpaca")
    state_machine = test_order_state_machine("alpaca")

    assert internal_order["internal_order_id"]
    assert request["passed"] is True
    assert request["order_submission_enabled"] is False
    assert response["passed"] is True
    assert set(response["tested_statuses"]) >= {"accepted", "partial_fill", "filled", "rejected", "canceled"}
    assert errors["passed"] is True
    assert "RATE_LIMITED" in errors["tested_errors"]
    assert idempotency["passed"] is True
    assert idempotency["duplicate_order_protection"] is True
    assert state_machine["passed"] is True
    assert state_machine["sandbox_submission_enabled"] is False
    assert state_machine["real_submission_enabled"] is False
    for item in [internal_order, request, response, errors, idempotency, state_machine]:
        assert item["mock_contract_only"] is True
        assert _is_safe(item)


def test_mock_contract_safety_validator_blocks_runtime_sandbox_account_and_order_paths():
    from provider_mock_contract.mock_contract_safety_validator import build_mock_contract_safety_summary, validate_mock_contract_safety

    assert build_mock_contract_safety_summary()["safe"] is True
    assert validate_mock_contract_safety({"mock_contract_runtime_enabled": True})["safe"] is False
    assert validate_mock_contract_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_mock_contract_safety({"account_read_enabled": True})["safe"] is False
    assert validate_mock_contract_safety({"order_submission_enabled": True})["safe"] is False
    assert validate_mock_contract_safety({"payload": "token=demo"})["safe"] is False
    assert validate_mock_contract_safety({"payload": "raw provider payload"})["safe"] is False


def test_mock_contract_orchestrator_summary_passes_or_warns():
    from provider_mock_contract.mock_contract_test_orchestrator import run_mock_contract_tests, summarize_mock_contract_results

    results = run_mock_contract_tests("alpaca")
    summary = summarize_mock_contract_results(results)
    assert summary["total_tests"] >= 7
    assert summary["failed"] == 0
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert summary["mock_contract_only"] is True
    assert _is_safe(summary)


def test_provider_mock_contract_api_endpoints_return_safe_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/provider-mock-contract/status",
        "/api/v5/provider-mock-contract/payloads",
        "/api/v5/provider-mock-contract/schema-validation",
        "/api/v5/provider-mock-contract/request-mapping",
        "/api/v5/provider-mock-contract/response-normalization",
        "/api/v5/provider-mock-contract/error-mapping",
        "/api/v5/provider-mock-contract/idempotency",
        "/api/v5/provider-mock-contract/state-machine",
        "/api/v5/provider-mock-contract/safety",
        "/api/v5/provider-mock-contract/summary",
    ]

    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "mock_contract_only" in encoded
        assert "paper_trading" in encoded
        for key in FALSE_KEYS:
            assert key in encoded
        assert _is_safe(payload)


def test_mock_contract_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from provider_mock_contract.provider_mock_contract_report import generate_provider_mock_contract_report

    report = generate_provider_mock_contract_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_22_provider_mock_contract_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["mock_contract_only"] is True
    assert report["summary"]["provider"] == "alpaca"
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "safety"], ["--check", "schema"], ["--check", "state-machine"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v522_provider_mock_contract.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["mock_contract_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-provider-mock-contract/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_PROVIDER_MOCK_CONTRACT.md")
    scanner = _read("runtime/security_scan.py")

    for name in [
        "fetchV5ProviderMockContractStatus",
        "fetchV5ProviderMockContractPayloads",
        "fetchV5ProviderMockContractSchemaValidation",
        "fetchV5ProviderMockContractRequestMapping",
        "fetchV5ProviderMockContractResponseNormalization",
        "fetchV5ProviderMockContractErrorMapping",
        "fetchV5ProviderMockContractIdempotency",
        "fetchV5ProviderMockContractStateMachine",
        "fetchV5ProviderMockContractSafety",
        "fetchV5ProviderMockContractSummary",
    ]:
        assert name in api_client
    for label in [
        "Mock Contract Status",
        "Mock Payload Catalog",
        "Schema Validation",
        "Request Mapping Test",
        "Response Normalization Test",
        "Error Mapping Test",
        "Idempotency Test",
        "Order State Machine Test",
        "Safety Validation",
        "Final Summary",
    ]:
        assert label in page
    assert "mock contract only" in page.lower()
    assert "mock contract runtime disabled" in page.lower()
    assert "sandbox api disabled" in page.lower()
    assert "account read disabled" in page.lower()
    assert "order submission disabled" in page.lower()
    assert "broker connected false" in page.lower()
    assert "real money disabled" in page.lower()
    assert "paper trading only" in page.lower()
    assert "V5 Mock Contract" in shell
    assert "no sandbox api connection" in docs.lower()
    assert "scan_provider_mock_contract_outputs" in scanner


def test_no_broker_sdk_network_or_order_calls_in_mock_contract_modules():
    root = Path("provider_mock_contract")
    assert root.exists()
    combined = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.py")).lower()
    forbidden = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "requests.",
        "httpx.",
        "urllib.request",
        "socket.",
        "submit_order(",
        "place_order(",
        "live_order(",
        "create_api_key",
        "read_account",
        "account_id=",
        "order_id=",
        "https://",
    ]
    for term in forbidden:
        assert term not in combined


def test_all_previous_v5_test_files_exist_through_v521():
    expected = [
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
        "tests/test_v517_integration_test_harness.py",
        "tests/test_v518_transition_blueprint.py",
        "tests/test_v519_provider_selection.py",
        "tests/test_v520_provider_onboarding.py",
        "tests/test_v521_provider_connector_design.py",
    ]
    for path in expected:
        assert Path(path).exists()


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _is_safe(payload: object) -> bool:
    encoded = json.dumps(payload, default=str).lower()
    forbidden = [
        "plaintext_secret",
        "raw_secret",
        "raw_token",
        "raw_api_key",
        "private_key",
        "authorization:",
        "bearer ",
        "sk-",
        "account_id=",
        "order_id=",
        "raw provider response:",
        "raw provider payload:",
        "provider endpoint url",
    ]
    return all(term not in encoded for term in forbidden)

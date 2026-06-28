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


def test_connector_contract_config_defaults_are_contract_only():
    from config.v5_sandbox_connector_contract_config import get_connector_contract_status

    status = get_connector_contract_status()

    assert status["connector_contract_mode"] == "contract_only"
    assert status["connector_provider"] == "none"
    assert status["contract_only"] is True
    assert status["connector_runtime_enabled"] is False
    assert status["real_sandbox_api_enabled"] is False
    assert status["broker_connected"] is False
    assert status["real_orders_enabled"] is False
    assert status["real_money_enabled"] is False
    assert status["paper_trading"] is True
    assert status["simulation_only"] is True
    assert _is_safe(status)


def test_connector_interface_contract_is_runtime_disabled():
    from sandbox_connector.connector_interface_contract import ConnectorInterfaceContract, build_interface_contract

    contract = ConnectorInterfaceContract()
    interface = build_interface_contract()

    assert interface["contract_only"] is True
    assert interface["connector_runtime_enabled"] is False
    assert interface["methods"] == ["get_account", "get_positions", "submit_order", "cancel_order", "get_order_status", "get_recent_orders", "health_check"]
    assert contract.health_check()["contract_only"] is True
    assert contract.submit_order({})["error_code"] == "CONNECTOR_DISABLED"
    assert contract.get_account()["broker_connected"] is False
    assert _is_safe(interface)


def test_request_schema_contract_sanitizes_and_validates_requests():
    from sandbox_connector.request_schema_contract import SubmitOrderRequest, sanitize_request, validate_submit_order_request

    request = SubmitOrderRequest.create(symbol="AAPL", side="BUY", quantity=5)
    payload = request.to_dict()

    assert validate_submit_order_request(payload)["valid"] is True
    assert "account_id" not in payload
    assert "broker_order_id" not in payload
    assert sanitize_request({**payload, "note": "token=abc"})["note"] == "[redacted]"
    assert _is_safe(payload)


def test_response_schema_contract_sanitizes_and_blocks_raw_provider_response():
    from sandbox_connector.response_schema_contract import build_order_response, sanitize_response, validate_response_contract

    response = build_order_response("client-1")
    dirty = sanitize_response({**response, "raw_provider_response": {"x": "y"}, "note": "secret=abc"})

    assert response["provider_order_ref"] == "planned_ref"
    assert response["raw_response_available"] is False
    assert response["sanitized"] is True
    assert "raw_provider_response" not in dirty
    assert dirty["note"] == "[redacted]"
    assert validate_response_contract(response)["valid"] is True
    assert _is_safe(response)


def test_error_code_contract_sanitizes_provider_errors():
    from sandbox_connector.error_code_contract import get_error_code_detail, list_error_codes, normalize_provider_error

    codes = list_error_codes()
    normalized = normalize_provider_error("planned", "secret=abc timeout raw payload")

    assert "CONNECTOR_DISABLED" in codes
    assert "ORDER_REJECTED" in codes
    assert get_error_code_detail("TIMEOUT")["retryable"] is True
    assert normalized["code"] in codes
    assert "secret" not in normalized["message"].lower()
    assert "raw payload" not in normalized["message"].lower()
    assert _is_safe(normalized)


def test_idempotency_policy_generates_stable_duplicate_safe_keys():
    from sandbox_connector.idempotency_policy import detect_duplicate_request, generate_idempotency_key, validate_idempotency_key

    payload = {"client_order_id": "client-1", "action": "submit", "created_at": "2026-01-01T09:31:22Z"}
    key_one = generate_idempotency_key(payload)
    key_two = generate_idempotency_key(payload)

    assert key_one == key_two
    assert validate_idempotency_key(key_one)["valid"] is True
    assert detect_duplicate_request(key_one, {key_one})["duplicate_detected"] is True
    assert detect_duplicate_request(key_one, {key_one})["error_code"] == "ORDER_DUPLICATE"
    assert _is_safe({"key": key_one})


def test_rate_limit_and_retry_policies_are_local_only():
    from sandbox_connector.rate_limit_policy import build_backoff_schedule, check_rate_limit
    from sandbox_connector.retry_policy import next_retry_delay, should_retry

    assert check_rate_limit("submit_order", request_count=6, window_seconds=60)["error_code"] == "RATE_LIMITED"
    assert build_backoff_schedule()["schedule_seconds"] == [1, 2, 4]
    assert should_retry("TIMEOUT", attempt=1)["retry"] is True
    assert should_retry("ORDER_REJECTED", attempt=1)["retry"] is False
    assert next_retry_delay("PROVIDER_UNAVAILABLE", attempt=2)["delay_seconds"] == 2


def test_credential_boundary_and_safety_validator_block_sensitive_payloads():
    from sandbox_connector.connector_safety_validator import build_connector_readiness_summary, validate_connector_contract, validate_no_runtime_connection
    from sandbox_connector.credential_boundary_contract import build_credential_boundary_contract, validate_no_credentials

    boundary = build_credential_boundary_contract()
    valid = validate_no_credentials({"client_order_id": "client-1"})
    invalid = validate_no_credentials({"note": "password=abc"})
    safety = validate_connector_contract()
    readiness = build_connector_readiness_summary()

    assert boundary["credential_handle_only"] is True
    assert valid["valid"] is True
    assert invalid["valid"] is False
    assert validate_no_runtime_connection()["safe"] is True
    assert safety["safe"] is True
    assert readiness["contract_only"] is True
    assert readiness["broker_connected"] is False
    assert readiness["real_orders_enabled"] is False
    assert _is_safe(boundary)


def test_sandbox_connector_contract_api_endpoints_are_safe():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/sandbox-connector/status",
        "/api/v5/sandbox-connector/interface-contract",
        "/api/v5/sandbox-connector/request-schema",
        "/api/v5/sandbox-connector/response-schema",
        "/api/v5/sandbox-connector/error-codes",
        "/api/v5/sandbox-connector/idempotency",
        "/api/v5/sandbox-connector/rate-limit",
        "/api/v5/sandbox-connector/retry-policy",
        "/api/v5/sandbox-connector/credential-boundary",
        "/api/v5/sandbox-connector/readiness",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "contract_only" in encoded
        assert "connector_runtime_enabled" in encoded
        assert "real_sandbox_api_enabled" in encoded
        assert "broker_connected" in encoded
        assert "real_orders_enabled" in encoded
        assert "real_money_enabled" in encoded
        assert "paper_trading" in encoded
        assert _is_safe(payload)


def test_sandbox_connector_contract_report_and_cli_can_run():
    from sandbox_connector.sandbox_connector_contract_report import generate_sandbox_connector_contract_report

    report = generate_sandbox_connector_contract_report()
    assert report["path"].endswith("reports/v5_13_sandbox_connector_contract_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(report)

    completed = subprocess.run(
        [sys.executable, "scripts/run_v513_sandbox_connector_contract.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert payload["summary"]["contract_only"] is True
    assert _is_safe(payload)


def test_frontend_docs_review_and_security_scan_include_v513():
    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-sandbox-connector/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5SandboxConnectorStatus" in api_client
    assert "fetchV5SandboxConnectorInterfaceContract" in api_client
    assert "fetchV5SandboxConnectorRequestSchema" in api_client
    assert "fetchV5SandboxConnectorResponseSchema" in api_client
    assert "fetchV5SandboxConnectorErrorCodes" in api_client
    assert "fetchV5SandboxConnectorIdempotency" in api_client
    assert "fetchV5SandboxConnectorRateLimit" in api_client
    assert "fetchV5SandboxConnectorRetryPolicy" in api_client
    assert "fetchV5SandboxConnectorCredentialBoundary" in api_client
    assert "fetchV5SandboxConnectorReadiness" in api_client
    assert "Sandbox Connector Contract Status" in page
    assert "Contract only" in page
    assert "Connector runtime: disabled" in page
    assert "Sandbox API: disabled" in page
    assert "Broker connected: false" in page
    assert "Real orders: disabled" in page
    assert "Real money: disabled" in page
    assert "Paper trading only" in page
    assert "V5 Sandbox Connector" in shell
    assert "/v5-sandbox-connector" in shell
    assert "V5.13" in _read("docs/V5_SANDBOX_CONNECTOR_CONTRACT.md")
    assert "V5.13" in _read("README.md")
    assert "V5.13" in _read("REVIEW_PACKAGE.md")
    assert "scan_sandbox_connector_outputs" in _read("runtime/security_scan.py")
    assert _is_safe(page)


def test_existing_v5_stack_tests_are_available_through_v512():
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
    ]
    for path in required_tests:
        assert Path(path).exists()


def test_no_real_broker_sdk_network_or_live_order_routing_is_introduced():
    planned_files = [
        "config/v5_sandbox_connector_contract_config.py",
        "sandbox_connector/connector_interface_contract.py",
        "sandbox_connector/request_schema_contract.py",
        "sandbox_connector/response_schema_contract.py",
        "sandbox_connector/error_code_contract.py",
        "sandbox_connector/idempotency_policy.py",
        "sandbox_connector/rate_limit_policy.py",
        "sandbox_connector/retry_policy.py",
        "sandbox_connector/credential_boundary_contract.py",
        "sandbox_connector/connector_safety_validator.py",
        "sandbox_connector/sandbox_connector_contract_report.py",
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

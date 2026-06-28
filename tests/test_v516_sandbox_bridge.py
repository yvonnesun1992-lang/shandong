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


def test_bridge_core_is_simulated_and_does_not_connect():
    from sandbox_bridge.sandbox_bridge_core import SandboxBridgeCore

    bridge = SandboxBridgeCore()
    connection = bridge.connect()
    sent = bridge.send_request({"action": "submit_order", "symbol": "AAPL", "quantity": 1})
    received = bridge.receive_response({"status": "accepted"})

    assert connection["bridge_only"] is True
    assert connection["real_connection"] is False
    assert bridge.is_connected() is False
    assert sent["network_call_attempted"] is False
    assert sent["real_connection"] is False
    assert received["sanitized"] is True
    assert _is_safe({"connection": connection, "sent": sent, "received": received})


def test_request_transformer_and_response_normalizer_are_sanitized():
    from sandbox_bridge.request_transformer import transform_account_request, transform_cancel_order, transform_position_request, transform_submit_order
    from sandbox_bridge.response_normalizer import normalize_account_response, normalize_error_response, normalize_order_response, normalize_position_response

    submit = transform_submit_order({"client_order_id": "client-1", "symbol": "MSFT", "side": "BUY", "quantity": 2, "note": "secret=abc"})
    cancel = transform_cancel_order({"client_order_id": "client-1", "account_id": "bad"})
    account = transform_account_request({"account_id": "bad"})
    positions = transform_position_request({"symbol": "MSFT", "token": "bad"})
    order_response = normalize_order_response({"raw_provider_response": {"x": "y"}, "broker_order_id": "bad", "status": "filled"})
    account_response = normalize_account_response({"account_id": "bad", "cash": 100})
    position_response = normalize_position_response({"positions": [{"symbol": "MSFT"}]})
    error_response = normalize_error_response({"stack": "secret=abc", "message": "timeout"})

    assert submit["sandbox_internal_format"] is True
    assert cancel["sandbox_internal_format"] is True
    assert account["request_type"] == "account"
    assert positions["request_type"] == "positions"
    assert "account_id" not in json.dumps({"submit": submit, "cancel": cancel, "account": account, "positions": positions}).lower()
    assert order_response["raw_response_available"] is False
    assert order_response["sanitized"] is True
    assert "raw_provider_response" not in order_response
    assert account_response["sanitized"] is True
    assert position_response["sanitized"] is True
    assert error_response["sanitized"] is True
    assert _is_safe({"submit": submit, "cancel": cancel, "account": account, "positions": positions, "order": order_response, "error": error_response})


def test_error_translation_retry_and_idempotency_layers():
    from sandbox_bridge.error_translation_layer import translate_error
    from sandbox_bridge.idempotency_enforcer import IdempotencyEnforcer
    from sandbox_bridge.retry_orchestrator import compute_backoff, schedule_retry, should_retry

    timeout = translate_error({"type": "timeout", "detail": "secret=abc"})
    rate_limit = translate_error({"type": "rate limit"})
    rejected = translate_error({"type": "order rejected"})
    unknown = translate_error({"type": "something else"})
    enforcer = IdempotencyEnforcer()
    request = {"symbol": "AAPL", "side": "BUY", "quantity": 1}
    key = enforcer.generate_key(request)
    first = enforcer.record_request(request, {"status": "MOCK_ACCEPTED"})
    duplicate = enforcer.check_duplicate(request)

    assert timeout["error_code"] == "TIMEOUT"
    assert rate_limit["error_code"] == "RATE_LIMITED"
    assert rejected["error_code"] == "ORDER_REJECTED"
    assert unknown["error_code"] == "UNKNOWN_ERROR"
    assert should_retry("TIMEOUT") is True
    assert should_retry("RATE_LIMITED") is True
    assert should_retry("ORDER_REJECTED") is False
    assert compute_backoff(2) == 4
    assert schedule_retry("TIMEOUT", 1)["delay_seconds"] == 2
    assert key
    assert first["recorded"] is True
    assert duplicate["duplicate"] is True
    assert duplicate["cached_response"]["status"] == "MOCK_ACCEPTED"
    assert _is_safe({"timeout": timeout, "duplicate": duplicate})


def test_session_router_and_safety_gate_are_bridge_only():
    from sandbox_bridge.bridge_safety_gate import validate_bridge_safety
    from sandbox_bridge.sandbox_router import route_request, select_backend
    from sandbox_bridge.sandbox_session import SandboxSession

    session = SandboxSession()
    started = session.start_session()
    refreshed = session.refresh_session()
    ended = session.end_session()
    routed_mock = route_request({"backend": "mock", "symbol": "AAPL", "side": "BUY", "quantity": 1})
    routed_skeleton = route_request({"backend": "ibkr_skeleton", "symbol": "AAPL"})
    selected = select_backend({"preferred": "bridge"})
    safe = validate_bridge_safety({"bridge_only": True})
    blocked_connection = validate_bridge_safety({"real_connection": True})
    blocked_url = validate_bridge_safety({"sandbox_api_url": "https://sandbox.example.com"})

    assert started["state"] == "CONNECTED_SIMULATED"
    assert refreshed["simulated_only"] is True
    assert ended["state"] == "DISCONNECTED"
    assert routed_mock["backend"] == "mock"
    assert routed_mock["real_connection"] is False
    assert routed_skeleton["status"] == "skeleton_only_rejected"
    assert selected["backend"] == "bridge"
    assert safe["safe"] is True
    assert blocked_connection["safe"] is False
    assert blocked_url["safe"] is False
    assert _is_safe({"started": started, "routed_mock": routed_mock, "safe": safe, "blocked_connection": blocked_connection})


def test_sandbox_bridge_api_endpoints_return_boundary_flags():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/sandbox-bridge/status",
        "/api/v5/sandbox-bridge/session",
        "/api/v5/sandbox-bridge/routing",
        "/api/v5/sandbox-bridge/transform",
        "/api/v5/sandbox-bridge/normalize",
        "/api/v5/sandbox-bridge/retry",
        "/api/v5/sandbox-bridge/idempotency",
        "/api/v5/sandbox-bridge/safety",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "bridge_only" in encoded
        assert "real_connection" in encoded
        assert "false" in encoded
        assert "paper_trading" in encoded
        assert _is_safe(payload)


def test_report_cli_frontend_docs_and_navigation_are_present():
    from sandbox_bridge.sandbox_bridge_report import generate_sandbox_bridge_report

    report = generate_sandbox_bridge_report("route")
    assert report["path"].endswith("reports/v5_16_sandbox_connector_bridge_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["summary"]["bridge_only"] is True

    for args in [["--test", "route"], ["--test", "transform"], ["--test", "normalize"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v516_sandbox_bridge.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
        assert payload["summary"]["bridge_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-sandbox-bridge/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5SandboxBridgeStatus" in api_client
    assert "fetchV5SandboxBridgeSession" in api_client
    assert "fetchV5SandboxBridgeRouting" in api_client
    assert "fetchV5SandboxBridgeTransform" in api_client
    assert "fetchV5SandboxBridgeNormalize" in api_client
    assert "fetchV5SandboxBridgeRetry" in api_client
    assert "fetchV5SandboxBridgeIdempotency" in api_client
    assert "fetchV5SandboxBridgeSafety" in api_client
    assert "Bridge Status" in page
    assert "Session Lifecycle" in page
    assert "Routing Layer" in page
    assert "Request Transform" in page
    assert "Response Normalize" in page
    assert "Error Translation" in page
    assert "Retry Policy" in page
    assert "Idempotency" in page
    assert "Safety Gate" in page
    assert "no real connection" in page.lower()
    assert "no broker" in page.lower()
    assert "no sandbox API" in page
    assert "paper trading only" in page.lower()
    assert "V5 Sandbox Bridge" in shell
    assert "/v5-sandbox-bridge" in shell
    assert "V5.16" in _read("docs/V5_SANDBOX_CONNECTOR_BRIDGE.md")
    assert "V5.16" in _read("README.md")
    assert "V5.16" in _read("REVIEW_PACKAGE.md")
    assert "scan_sandbox_bridge_outputs" in _read("runtime/security_scan.py")
    assert _is_safe(page)


def test_existing_v5_stack_tests_are_available_through_v515():
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
    ]:
        assert Path(path).exists()


def test_no_sdk_network_or_real_runtime_strings_in_bridge_modules():
    planned_files = [
        "sandbox_bridge/sandbox_bridge_core.py",
        "sandbox_bridge/request_transformer.py",
        "sandbox_bridge/response_normalizer.py",
        "sandbox_bridge/error_translation_layer.py",
        "sandbox_bridge/retry_orchestrator.py",
        "sandbox_bridge/idempotency_enforcer.py",
        "sandbox_bridge/sandbox_session.py",
        "sandbox_bridge/sandbox_router.py",
        "sandbox_bridge/bridge_safety_gate.py",
        "sandbox_bridge/sandbox_bridge_report.py",
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

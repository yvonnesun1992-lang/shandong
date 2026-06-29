from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}
FALSE_KEYS = [
    "connector_runtime_enabled",
    "sandbox_api_enabled",
    "account_read_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_connector_design_config_defaults_and_blocks_real_path_env(monkeypatch):
    from config.v5_provider_connector_design_config import (
        get_connector_design_mode,
        get_connector_design_status,
        get_design_provider,
    )

    assert get_connector_design_mode() == "design_only"
    assert get_design_provider() in PROVIDERS
    status = get_connector_design_status()

    assert status["design_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_CONNECTOR_RUNTIME", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ACCOUNT_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_connector_design_status()

    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "connector runtime requested but blocked in v5.21" in warnings
    assert "sandbox api requested but blocked in v5.21" in warnings
    assert "account read requested but blocked in v5.21" in warnings
    assert "order submission requested but blocked in v5.21" in warnings
    assert "real money requested but blocked in v5.21" in warnings
    assert _is_safe(blocked)


def test_connector_design_provider_fallback(monkeypatch):
    from config.v5_provider_connector_design_config import get_design_provider

    monkeypatch.setenv("SHANDONG_V5_CONNECTOR_DESIGN_PROVIDER", "ibkr")
    assert get_design_provider() == "ibkr"
    monkeypatch.setenv("SHANDONG_V5_CONNECTOR_DESIGN_PROVIDER", "unknown")
    assert get_design_provider() == "alpaca"


def test_field_order_response_account_error_policy_and_state_designs_exist():
    from provider_connector_design.account_position_mapping import build_account_position_mapping
    from provider_connector_design.connector_safety_boundary import build_connector_safety_boundary
    from provider_connector_design.idempotency_policy import build_idempotency_policy
    from provider_connector_design.order_request_mapping import build_order_request_mapping
    from provider_connector_design.order_response_mapping import build_order_response_mapping
    from provider_connector_design.order_state_machine_design import build_order_state_machine_design
    from provider_connector_design.provider_error_mapping import build_provider_error_mapping
    from provider_connector_design.provider_field_mapping import build_provider_field_mapping
    from provider_connector_design.rate_limit_policy import build_rate_limit_policy

    field_mapping = build_provider_field_mapping("alpaca")
    request = build_order_request_mapping("alpaca")
    response = build_order_response_mapping("alpaca")
    account_position = build_account_position_mapping("alpaca")
    errors = build_provider_error_mapping("alpaca")
    rate_limit = build_rate_limit_policy("alpaca")
    idempotency = build_idempotency_policy("alpaca")
    state_machine = build_order_state_machine_design("alpaca")
    safety = build_connector_safety_boundary()

    assert len(field_mapping["field_mappings"]) >= 10
    assert "internal_order_id" in request["required_internal_fields"]
    assert request["order_submission_enabled"] is False
    assert response["raw_response_policy"] == "redacted_only"
    assert response["response_mapping"]["raw_response_redacted"] == "placeholder_redacted_only"
    assert account_position["real_account_read_enabled"] is False
    assert account_position["sandbox_account_read_enabled"] is False
    assert all("placeholder" in str(value).lower() for value in account_position["account_mapping"].values())
    assert "AUTH_ERROR" in errors["error_mapping"]
    assert rate_limit["network_calls_enabled"] is False
    assert idempotency["duplicate_order_protection"] is True
    assert idempotency["order_submission_enabled"] is False
    assert "SUBMISSION_BLOCKED" in state_machine["states"]
    assert state_machine["sandbox_submission_enabled"] is False
    assert state_machine["real_submission_enabled"] is False
    assert safety["safe"] is True
    for item in [field_mapping, request, response, account_position, errors, rate_limit, idempotency, state_machine, safety]:
        assert item["design_only"] is True
        assert _is_safe(item)


def test_connector_safety_validator_blocks_runtime_sandbox_account_and_order_paths():
    from provider_connector_design.connector_safety_boundary import (
        validate_connector_design_safety,
        build_connector_safety_boundary,
    )

    assert build_connector_safety_boundary()["safe"] is True
    assert validate_connector_design_safety({"connector_runtime_enabled": True})["safe"] is False
    assert validate_connector_design_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_connector_design_safety({"account_read_enabled": True})["safe"] is False
    assert validate_connector_design_safety({"order_submission_enabled": True})["safe"] is False
    assert validate_connector_design_safety({"payload": "token=demo"})["safe"] is False
    assert validate_connector_design_safety({"payload": "raw provider response"})["safe"] is False


def test_provider_connector_design_api_endpoints_return_safe_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/provider-connector-design/status",
        "/api/v5/provider-connector-design/field-mapping",
        "/api/v5/provider-connector-design/order-request",
        "/api/v5/provider-connector-design/order-response",
        "/api/v5/provider-connector-design/account-position",
        "/api/v5/provider-connector-design/error-mapping",
        "/api/v5/provider-connector-design/rate-limit",
        "/api/v5/provider-connector-design/idempotency",
        "/api/v5/provider-connector-design/state-machine",
        "/api/v5/provider-connector-design/safety",
    ]

    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "design_only" in encoded
        assert "paper_trading" in encoded
        for key in FALSE_KEYS:
            assert key in encoded
        assert _is_safe(payload)


def test_connector_design_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from provider_connector_design.provider_connector_design_report import generate_provider_connector_design_report

    report = generate_provider_connector_design_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_21_provider_connector_design_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["design_only"] is True
    assert report["summary"]["design_provider"] == "alpaca"
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "safety"], ["--check", "state-machine"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v521_provider_connector_design.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["design_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-provider-connector-design/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_PROVIDER_CONNECTOR_DESIGN.md")
    scanner = _read("runtime/security_scan.py")

    for name in [
        "fetchV5ProviderConnectorDesignStatus",
        "fetchV5ProviderConnectorDesignFieldMapping",
        "fetchV5ProviderConnectorDesignOrderRequest",
        "fetchV5ProviderConnectorDesignOrderResponse",
        "fetchV5ProviderConnectorDesignAccountPosition",
        "fetchV5ProviderConnectorDesignErrorMapping",
        "fetchV5ProviderConnectorDesignRateLimit",
        "fetchV5ProviderConnectorDesignIdempotency",
        "fetchV5ProviderConnectorDesignStateMachine",
        "fetchV5ProviderConnectorDesignSafety",
    ]:
        assert name in api_client
    for label in [
        "Connector Design Status",
        "Field Mapping",
        "Order Request Mapping",
        "Order Response Mapping",
        "Account / Position Mapping",
        "Error Mapping",
        "Rate Limit Policy",
        "Idempotency Policy",
        "Order State Machine",
        "Safety Boundary",
    ]:
        assert label in page
    assert "design only" in page.lower()
    assert "connector runtime disabled" in page.lower()
    assert "sandbox api disabled" in page.lower()
    assert "account read disabled" in page.lower()
    assert "order submission disabled" in page.lower()
    assert "broker connected false" in page.lower()
    assert "real money disabled" in page.lower()
    assert "paper trading only" in page.lower()
    assert "V5 Connector Design" in shell
    assert "no sandbox api connection" in docs.lower()
    assert "scan_provider_connector_design_outputs" in scanner


def test_no_broker_sdk_network_or_order_calls_in_connector_design_modules():
    root = Path("provider_connector_design")
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


def test_all_previous_v5_test_files_exist_through_v520():
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
        "provider endpoint url",
    ]
    return all(term not in encoded for term in forbidden)

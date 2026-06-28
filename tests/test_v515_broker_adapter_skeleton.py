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
    "account_id",
    "real_order_id",
    "/users/apple",
]


def test_base_and_skeleton_adapters_never_connect_or_trade():
    from broker_adapter.alpaca_skeleton_adapter import AlpacaSkeletonAdapter
    from broker_adapter.base_adapter import BrokerAdapterBase
    from broker_adapter.ibkr_skeleton_adapter import IBKRSkeletonAdapter

    base = BrokerAdapterBase()
    for method in [base.connect, base.disconnect, base.is_connected, base.get_account, base.get_positions]:
        try:
            method()
            assert False, "base methods must raise"
        except NotImplementedError:
            pass

    for adapter in [IBKRSkeletonAdapter(), AlpacaSkeletonAdapter()]:
        connect = adapter.connect()
        order = adapter.submit_order({"symbol": "AAPL", "side": "BUY", "quantity": 1})
        account = adapter.get_account()
        positions = adapter.get_positions()

        assert connect["status"] == "skeleton_only"
        assert order["status"] == "skeleton_only_rejected"
        assert account["status"] == "skeleton_only"
        assert positions["positions"] == []
        assert connect["real_connection"] is False
        assert order["real_orders"] is False
        assert order["paper_trading"] is True
        assert _is_safe({"connect": connect, "order": order, "account": account, "positions": positions})


def test_registry_and_factory_create_expected_adapter_types():
    from broker_adapter.adapter_factory import create_broker_adapter
    from broker_adapter.adapter_registry import build_default_registry
    from broker_adapter.mock_adapter import MockBrokerAdapter

    registry = build_default_registry()
    names = registry.list_adapters()

    assert {"mock", "ibkr_skeleton", "alpaca_skeleton", "futu_skeleton", "tiger_skeleton", "schwab_skeleton"}.issubset(names)
    assert isinstance(create_broker_adapter("mock"), MockBrokerAdapter)
    assert create_broker_adapter("ibkr_skeleton").connect()["adapter"] == "ibkr_skeleton"
    assert create_broker_adapter("alpaca_skeleton").connect()["adapter"] == "alpaca_skeleton"
    assert create_broker_adapter("futu_skeleton").connect()["adapter"] == "futu_skeleton"
    assert create_broker_adapter("tiger_skeleton").connect()["adapter"] == "tiger_skeleton"
    assert create_broker_adapter("schwab_skeleton").connect()["adapter"] == "schwab_skeleton"


def test_capability_matrix_and_compatibility_layer_are_structure_only():
    from broker_adapter.capability_matrix import build_capability_matrix
    from broker_adapter.compatibility_layer import (
        detect_missing_methods,
        map_mock_to_skeleton_schema,
        validate_contract_alignment,
        validate_interface_compatibility,
    )

    matrix = build_capability_matrix()
    compatibility = validate_interface_compatibility()
    mapping = map_mock_to_skeleton_schema()
    missing = detect_missing_methods()
    alignment = validate_contract_alignment()

    assert matrix["mock"]["supports_market_order"] is True
    assert matrix["ibkr_skeleton"]["supports_market_order"] is False
    assert matrix["alpaca_skeleton"]["supports_streaming"] is False
    assert compatibility["compatible"] is True
    assert mapping["mock_only"] is True
    assert missing["missing_methods"] == []
    assert alignment["aligned"] is True
    assert _is_safe({"matrix": matrix, "compatibility": compatibility, "mapping": mapping, "alignment": alignment})


def test_safety_guard_blocks_real_connection_and_sensitive_config():
    from broker_adapter.safety_guard import validate_adapter_safety

    mock = validate_adapter_safety("mock", {"mock_only": True})
    skeleton = validate_adapter_safety("ibkr_skeleton", {"mode": "skeleton_only"})
    real_connection = validate_adapter_safety("ibkr_skeleton", {"real_connection": True})
    sensitive = validate_adapter_safety("mock", {"credential": "api_key=abc"})
    oauth = validate_adapter_safety("alpaca_skeleton", {"oauth_attempt": True})

    assert mock["safe"] is True
    assert skeleton["safe"] is True
    assert real_connection["safe"] is False
    assert sensitive["safe"] is False
    assert oauth["safe"] is False
    assert real_connection["blocked_real_connection"] is True
    assert skeleton["reason"] == "V5.15 skeleton only stage"
    assert _is_safe({"mock": mock, "skeleton": skeleton, "real_connection": real_connection, "oauth": oauth})


def test_broker_adapter_api_endpoints_return_skeleton_boundary_flags():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/broker-adapter/list",
        "/api/v5/broker-adapter/capabilities",
        "/api/v5/broker-adapter/registry",
        "/api/v5/broker-adapter/factory",
        "/api/v5/broker-adapter/safety",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "skeleton_only" in encoded
        assert "real_connection" in encoded
        assert "false" in encoded
        assert "paper_trading" in encoded
        assert _is_safe(payload)


def test_report_cli_frontend_docs_and_navigation_are_present():
    from broker_adapter.broker_adapter_report import generate_broker_adapter_report

    report = generate_broker_adapter_report()
    assert report["path"].endswith("reports/v5_15_broker_adapter_skeleton_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["summary"]["skeleton_only"] is True

    for args in [["--list"], ["--test", "ibkr_skeleton"], ["--test", "alpaca_skeleton"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v515_broker_adapter_skeleton.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
        assert payload["summary"]["skeleton_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-broker-adapter/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5BrokerAdapterList" in api_client
    assert "fetchV5BrokerAdapterCapabilities" in api_client
    assert "fetchV5BrokerAdapterRegistry" in api_client
    assert "fetchV5BrokerAdapterFactory" in api_client
    assert "fetchV5BrokerAdapterSafety" in api_client
    assert "Broker Adapter Registry" in page
    assert "Adapter Factory" in page
    assert "Capability Matrix" in page
    assert "Skeleton Adapters List" in page
    assert "Safety Guard Status" in page
    assert "Compatibility Layer Check" in page
    assert "Final Verdict" in page
    assert "skeleton only" in page.lower()
    assert "no real connection" in page.lower()
    assert "no real orders" in page.lower()
    assert "paper trading only" in page.lower()
    assert "V5 Broker Adapter" in shell
    assert "/v5-broker-adapter" in shell
    assert "V5.15" in _read("docs/V5_BROKER_ADAPTER_SKELETON.md")
    assert "V5.15" in _read("README.md")
    assert "V5.15" in _read("REVIEW_PACKAGE.md")
    assert "scan_broker_adapter_outputs" in _read("runtime/security_scan.py")
    assert _is_safe(page)


def test_existing_v5_stack_tests_are_available_through_v514():
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
    ]:
        assert Path(path).exists()


def test_no_broker_sdk_network_or_real_runtime_strings_in_adapter_modules():
    planned_files = [
        "broker_adapter/base_adapter.py",
        "broker_adapter/adapter_registry.py",
        "broker_adapter/adapter_factory.py",
        "broker_adapter/ibkr_skeleton_adapter.py",
        "broker_adapter/alpaca_skeleton_adapter.py",
        "broker_adapter/skeleton_adapters.py",
        "broker_adapter/mock_adapter.py",
        "broker_adapter/compatibility_layer.py",
        "broker_adapter/capability_matrix.py",
        "broker_adapter/safety_guard.py",
        "broker_adapter/broker_adapter_report.py",
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
        "authorization",
    ]
    for item in allowed:
        text = text.replace(item, "")
    return not any(term in text for term in SENSITIVE_TERMS)

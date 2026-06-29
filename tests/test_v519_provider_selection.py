from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}
FALSE_KEYS = [
    "provider_connection_enabled",
    "sandbox_api_enabled",
    "broker_connected",
    "real_orders_enabled",
    "real_money_enabled",
]


def test_provider_selection_config_defaults_and_blocks_env(monkeypatch):
    from config.v5_provider_selection_config import get_candidate_providers, get_provider_selection_mode, get_provider_selection_status

    assert get_provider_selection_mode() == "selection_only"
    assert set(get_candidate_providers()) == PROVIDERS
    status = get_provider_selection_status()

    assert status["selection_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_PROVIDER_CONNECTION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_ORDERS", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_provider_selection_status()

    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "provider connection requested but blocked in v5.19" in warnings
    assert "sandbox api requested but blocked in v5.19" in warnings
    assert "real orders requested but blocked in v5.19" in warnings
    assert "real money requested but blocked in v5.19" in warnings
    assert _is_safe(blocked)


def test_provider_universe_capability_and_risk_matrix():
    from provider_selection.provider_capability_matrix import build_provider_capability_matrix
    from provider_selection.provider_risk_matrix import build_provider_risk_matrix
    from provider_selection.provider_universe import build_provider_universe

    universe = build_provider_universe()
    capabilities = build_provider_capability_matrix()
    risks = build_provider_risk_matrix()

    assert {item["provider"] for item in universe["providers"]} == PROVIDERS
    assert len(capabilities["matrix"]) == len(PROVIDERS)
    assert len(risks["matrix"]) == len(PROVIDERS)
    for provider in universe["providers"]:
        assert provider["selection_only"] is True
        assert provider["real_connection_enabled"] is False
        assert provider["sandbox_api_enabled"] is False
        assert provider["credential_required"] is True
    for row in capabilities["matrix"]:
        assert row["selection_only"] is True
        assert row["real_connection_enabled"] is False
        assert row["score"] >= 0
    for row in risks["matrix"]:
        assert row["selection_only"] is True
        assert row["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
        assert row["risk_score"] >= 0
    assert _is_safe({"universe": universe, "capabilities": capabilities, "risks": risks})


def test_provider_preparation_checklists_are_not_ready():
    from provider_selection.account_preparation_checklist import build_account_preparation_checklist
    from provider_selection.api_permission_checklist import build_api_permission_checklist
    from provider_selection.compliance_checklist import build_compliance_checklist
    from provider_selection.market_data_permission_checklist import build_market_data_permission_checklist

    account = build_account_preparation_checklist("alpaca")
    api = build_api_permission_checklist("alpaca")
    market_data = build_market_data_permission_checklist("alpaca")
    compliance = build_compliance_checklist("alpaca")

    assert account["ready"] is False
    assert api["api_ready"] is False
    assert market_data["market_data_ready"] is False
    assert compliance["compliance_ready"] is False
    assert account["selection_only"] is True
    assert api["credential_storage_required"] == "future_vault"
    assert len(account["checklist"]) >= 10
    assert len(api["permissions"]) >= 10
    assert len(market_data["requirements"]) >= 10
    assert len(compliance["requirements"]) >= 10
    assert _is_safe({"account": account, "api": api, "market_data": market_data, "compliance": compliance})


def test_provider_ranking_recommends_provider_and_safety_blocks_real_paths():
    from provider_selection.provider_selection_safety_validator import (
        build_provider_selection_safety_summary,
        validate_no_credentials,
        validate_no_provider_connection,
        validate_provider_selection_safety,
    )
    from provider_selection.provider_selection_scoring import rank_providers, recommend_provider, score_provider

    scored = score_provider("alpaca")
    ranking = rank_providers(["alpaca", "ibkr", "futu", "tiger", "schwab"])
    recommendation = recommend_provider(["alpaca", "ibkr", "futu", "tiger", "schwab"])
    safety = build_provider_selection_safety_summary()

    assert scored["provider"] == "alpaca"
    assert scored["selection_only"] is True
    assert ranking["selection_only"] is True
    assert ranking["recommended_provider"] in PROVIDERS
    assert recommendation["recommended_provider"] in PROVIDERS
    assert safety["safe"] is True
    assert safety["selection_only"] is True
    assert validate_no_provider_connection()["safe"] is True
    assert validate_no_credentials({"payload": "safe"})["safe"] is True
    assert validate_no_credentials({"payload": "api_key=demo"})["safe"] is False
    assert validate_provider_selection_safety({"real_connection": True})["safe"] is False
    assert _is_safe({"scored": scored, "ranking": ranking, "recommendation": recommendation, "safety": safety})


def test_provider_selection_api_endpoints_return_safe_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/provider-selection/status",
        "/api/v5/provider-selection/universe",
        "/api/v5/provider-selection/capability-matrix",
        "/api/v5/provider-selection/risk-matrix",
        "/api/v5/provider-selection/account-checklist",
        "/api/v5/provider-selection/api-permissions",
        "/api/v5/provider-selection/market-data",
        "/api/v5/provider-selection/compliance",
        "/api/v5/provider-selection/ranking",
        "/api/v5/provider-selection/safety",
    ]

    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "selection_only" in encoded
        assert "paper_trading" in encoded
        for key in FALSE_KEYS:
            assert key in encoded
        assert _is_safe(payload)


def test_provider_selection_report_cli_frontend_docs_and_navigation_are_present():
    from provider_selection.provider_selection_report import generate_provider_selection_report

    report = generate_provider_selection_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_19_provider_selection_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["selection_only"] is True
    assert report["summary"]["ranking"]["recommended_provider"] in PROVIDERS

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--ranking"], ["--check", "safety"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v519_provider_selection.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["selection_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-provider-selection/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    for name in [
        "fetchV5ProviderSelectionStatus",
        "fetchV5ProviderSelectionUniverse",
        "fetchV5ProviderSelectionCapabilityMatrix",
        "fetchV5ProviderSelectionRiskMatrix",
        "fetchV5ProviderSelectionAccountChecklist",
        "fetchV5ProviderSelectionApiPermissions",
        "fetchV5ProviderSelectionMarketData",
        "fetchV5ProviderSelectionCompliance",
        "fetchV5ProviderSelectionRanking",
        "fetchV5ProviderSelectionSafety",
    ]:
        assert name in api_client
    for label in [
        "Provider Selection Status",
        "Provider Universe",
        "Capability Matrix",
        "Risk Matrix",
        "Account Preparation Checklist",
        "API Permission Checklist",
        "Market Data Checklist",
        "Compliance Checklist",
        "Provider Ranking",
        "Recommended Provider",
        "Safety Validation",
    ]:
        assert label in page
    assert "selection only" in page.lower()
    assert "provider connection disabled" in page.lower()
    assert "sandbox api disabled" in page.lower()
    assert "broker connected false" in page.lower()
    assert "real orders disabled" in page.lower()
    assert "real money disabled" in page.lower()
    assert "paper trading only" in page.lower()
    assert "V5 Provider Selection" in shell
    assert "/v5-provider-selection" in shell
    assert "V5.19" in _read("docs/V5_PROVIDER_SELECTION.md")
    assert "V5.19" in _read("README.md")
    assert "V5.19" in _read("REVIEW_PACKAGE.md")
    assert "scan_provider_selection_outputs" in _read("runtime/security_scan.py")
    assert _is_safe(page)


def test_no_sdk_network_or_real_runtime_strings_in_provider_selection_modules():
    planned_files = [
        "provider_selection/provider_universe.py",
        "provider_selection/provider_capability_matrix.py",
        "provider_selection/provider_risk_matrix.py",
        "provider_selection/account_preparation_checklist.py",
        "provider_selection/api_permission_checklist.py",
        "provider_selection/market_data_permission_checklist.py",
        "provider_selection/compliance_checklist.py",
        "provider_selection/provider_selection_scoring.py",
        "provider_selection/provider_selection_safety_validator.py",
        "provider_selection/provider_selection_report.py",
    ]
    forbidden = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "requests.",
        "httpx.",
        "place_order(",
        "live_order(",
        "submit_real",
        "read_account",
    ]
    for path in planned_files:
        text = _read(path)
        lowered = text.lower()
        assert "bfill(" not in lowered
        for term in forbidden:
            assert term.lower() not in lowered


def test_existing_v5_stack_tests_are_available_through_v518():
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
        "tests/test_v517_integration_test_harness.py",
        "tests/test_v518_transition_blueprint.py",
    ]:
        assert Path(path).exists()


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _is_safe(payload: object) -> bool:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    blocked = [
        "sk-",
        "gho_",
        "xoxb-",
        "authorization:",
        "bearer ",
        "account_id",
        "real_order_id",
        "raw provider response",
        "/users/apple",
        "broker credential",
    ]
    return not any(term in text for term in blocked)

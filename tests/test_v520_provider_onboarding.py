from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}
FALSE_KEYS = [
    "provider_portal_access_enabled",
    "api_key_creation_enabled",
    "sandbox_api_enabled",
    "broker_connected",
    "real_orders_enabled",
    "real_money_enabled",
]


def test_onboarding_config_defaults_and_blocks_real_path_env(monkeypatch):
    from config.v5_provider_onboarding_config import get_onboarding_mode, get_onboarding_status, get_selected_provider

    assert get_onboarding_mode() == "runbook_only"
    assert get_selected_provider() in PROVIDERS

    status = get_onboarding_status()
    assert status["runbook_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_PROVIDER_PORTAL_ACCESS", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_API_KEY_CREATION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_ORDERS", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_onboarding_status()

    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "provider portal access requested but blocked in v5.20" in warnings
    assert "sandbox api requested but blocked in v5.20" in warnings
    assert "api key creation requested but blocked in v5.20" in warnings
    assert "real orders requested but blocked in v5.20" in warnings
    assert "real money requested but blocked in v5.20" in warnings
    assert _is_safe(blocked)


def test_selected_provider_resolver_uses_v519_report_config_and_fallback(monkeypatch, tmp_path):
    from provider_onboarding.selected_provider_resolver import (
        build_selected_provider_summary,
        get_selected_provider_from_v519,
        resolve_selected_provider,
    )

    report = tmp_path / "v5_19_provider_selection_report.md"
    report.write_text("- Recommended provider: ibkr\n", encoding="utf-8")

    assert get_selected_provider_from_v519(report) == "ibkr"
    assert resolve_selected_provider(report_path=report)["selected_provider"] == "ibkr"
    assert resolve_selected_provider(report_path=report)["source"] == "v519_report"

    missing = tmp_path / "missing.md"
    monkeypatch.setenv("SHANDONG_V5_SELECTED_PROVIDER", "futu")
    assert resolve_selected_provider(report_path=missing)["selected_provider"] == "futu"
    assert resolve_selected_provider(report_path=missing)["source"] == "config"

    monkeypatch.setenv("SHANDONG_V5_SELECTED_PROVIDER", "unknown")
    fallback = resolve_selected_provider(report_path=missing)
    assert fallback["selected_provider"] == "alpaca"
    assert fallback["source"] == "fallback"

    summary = build_selected_provider_summary(report_path=report)
    assert summary["selected_provider"] == "ibkr"
    assert summary["runbook_only"] is True
    assert summary["broker_connected"] is False
    assert summary["sandbox_api_enabled"] is False
    assert _is_safe(summary)


def test_onboarding_runbooks_are_not_ready_and_are_runbook_only():
    from provider_onboarding.account_opening_runbook import build_account_opening_runbook
    from provider_onboarding.api_key_preparation_runbook import build_api_key_preparation_runbook
    from provider_onboarding.approval_risk_runbook import build_approval_risk_runbook
    from provider_onboarding.market_data_onboarding_runbook import build_market_data_onboarding_runbook
    from provider_onboarding.sandbox_access_runbook import build_sandbox_access_runbook
    from provider_onboarding.sandbox_dry_run_runbook import build_sandbox_dry_run_runbook

    account = build_account_opening_runbook("alpaca")
    sandbox = build_sandbox_access_runbook("alpaca")
    api_key = build_api_key_preparation_runbook("alpaca")
    market_data = build_market_data_onboarding_runbook("alpaca")
    approval = build_approval_risk_runbook("alpaca")
    dry_run = build_sandbox_dry_run_runbook("alpaca")

    assert account["ready"] is False
    assert sandbox["sandbox_access_ready"] is False
    assert api_key["api_key_ready"] is False
    assert market_data["market_data_ready"] is False
    assert approval["approval_risk_ready"] is False
    assert dry_run["dry_run_ready"] is False
    assert api_key["credential_storage"] == "future_vault"
    assert approval["manual_approval_required"] is True
    assert approval["kill_switch_required"] is True
    assert dry_run["sandbox_orders_enabled"] is False
    for runbook in [account, sandbox, api_key, market_data, approval, dry_run]:
        assert runbook["runbook_only"] is True
        assert len(runbook.get("steps", runbook.get("phases", []))) >= 10
        assert runbook["blocking_items"]
        assert _is_safe(runbook)


def test_onboarding_safety_validator_blocks_real_paths_and_credentials():
    from provider_onboarding.onboarding_safety_validator import (
        build_onboarding_safety_summary,
        validate_no_api_key_creation,
        validate_no_credentials,
        validate_no_portal_access,
        validate_no_sandbox_connection,
        validate_onboarding_safety,
    )

    summary = build_onboarding_safety_summary()
    assert summary["safe"] is True
    assert summary["runbook_only"] is True
    assert validate_no_portal_access({"provider_portal_access_enabled": False})["safe"] is True
    assert validate_no_api_key_creation({"api_key_creation_enabled": False})["safe"] is True
    assert validate_no_sandbox_connection({"sandbox_api_enabled": False})["safe"] is True
    assert validate_no_portal_access({"provider_portal_access_enabled": True})["safe"] is False
    assert validate_no_api_key_creation({"api_key_creation_enabled": True})["safe"] is False
    assert validate_no_sandbox_connection({"sandbox_api_enabled": True})["safe"] is False
    assert validate_no_credentials({"payload": "safe"})["safe"] is True
    assert validate_no_credentials({"payload": "token=demo"})["safe"] is False
    assert validate_no_credentials({"payload": "account_id=abc"})["safe"] is False
    assert validate_onboarding_safety({"real_orders_enabled": True})["safe"] is False
    assert _is_safe(summary)


def test_provider_onboarding_api_endpoints_return_safe_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/provider-onboarding/status",
        "/api/v5/provider-onboarding/selected-provider",
        "/api/v5/provider-onboarding/account-opening",
        "/api/v5/provider-onboarding/sandbox-access",
        "/api/v5/provider-onboarding/api-key",
        "/api/v5/provider-onboarding/market-data",
        "/api/v5/provider-onboarding/approval-risk",
        "/api/v5/provider-onboarding/sandbox-dry-run",
        "/api/v5/provider-onboarding/safety",
    ]

    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "runbook_only" in encoded
        assert "paper_trading" in encoded
        for key in FALSE_KEYS:
            assert key in encoded
        assert _is_safe(payload)


def test_onboarding_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from provider_onboarding.provider_onboarding_report import generate_provider_onboarding_report

    report = generate_provider_onboarding_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_20_provider_onboarding_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["runbook_only"] is True
    assert report["summary"]["selected_provider"]["selected_provider"] in PROVIDERS
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "safety"], ["--check", "dry-run"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v520_provider_onboarding.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["runbook_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-provider-onboarding/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_PROVIDER_ONBOARDING.md")
    scanner = _read("runtime/security_scan.py")

    for name in [
        "fetchV5ProviderOnboardingStatus",
        "fetchV5ProviderOnboardingSelectedProvider",
        "fetchV5ProviderOnboardingAccountOpening",
        "fetchV5ProviderOnboardingSandboxAccess",
        "fetchV5ProviderOnboardingApiKey",
        "fetchV5ProviderOnboardingMarketData",
        "fetchV5ProviderOnboardingApprovalRisk",
        "fetchV5ProviderOnboardingSandboxDryRun",
        "fetchV5ProviderOnboardingSafety",
    ]:
        assert name in api_client
    for label in [
        "Onboarding Status",
        "Selected Provider",
        "Account Opening Runbook",
        "Sandbox Access Runbook",
        "API Key Preparation",
        "Market Data Onboarding",
        "Approval & Risk",
        "Sandbox Dry Run",
        "Safety Validation",
        "Blocking Items",
    ]:
        assert label in page
    assert "runbook only" in page.lower()
    assert "provider portal access disabled" in page.lower()
    assert "api key creation disabled" in page.lower()
    assert "sandbox api disabled" in page.lower()
    assert "broker connected false" in page.lower()
    assert "real orders disabled" in page.lower()
    assert "real money disabled" in page.lower()
    assert "paper trading only" in page.lower()
    assert "V5 Provider Onboarding" in shell
    assert "no provider portal access" in docs.lower()
    assert "scan_provider_onboarding_outputs" in scanner


def test_no_broker_sdk_network_or_order_calls_in_onboarding_modules():
    root = Path("provider_onboarding")
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
        "place_order(",
        "submit_order(",
        "live_order(",
        "create_api_key",
        "read_account",
        "account_id=",
        "order_id=",
    ]
    for term in forbidden:
        assert term not in combined


def test_all_previous_v5_test_files_exist_through_v519():
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
        "provider portal session",
        "raw provider response",
    ]
    return all(term not in encoded for term in forbidden)

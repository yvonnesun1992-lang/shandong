from __future__ import annotations

import json
import subprocess
import sys

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
    "/users/apple",
]


def test_sandbox_config_defaults_are_planning_only():
    from config.v5_broker_sandbox_config import get_sandbox_readiness_status

    status = get_sandbox_readiness_status()

    assert status["sandbox_mode"] == "planned"
    assert status["sandbox_provider"] == "none"
    assert status["sandbox_connection_enabled"] is False
    assert status["sandbox_orders_enabled"] is False
    assert status["broker_connected"] is False
    assert status["real_orders_enabled"] is False
    assert status["real_money_enabled"] is False
    assert status["paper_trading"] is True
    assert status["planning_only"] is True
    assert _is_safe(status)


def test_sandbox_provider_plan_has_all_providers_without_sdk_imports():
    from sandbox.sandbox_provider_plan import build_sandbox_provider_plan, list_sandbox_provider_plans

    plans = list_sandbox_provider_plans()
    selected = build_sandbox_provider_plan("alpaca_sandbox_planned")

    assert len(plans) == 5
    assert selected["provider"] == "alpaca_sandbox_planned"
    assert selected["status"] == "planned_only"
    assert selected["credential_required"] is True
    assert selected["manual_approval_required"] is True
    assert selected["kill_switch_required"] is True
    assert selected["audit_required"] is True
    assert selected["sandbox_orders_enabled"] is False
    assert selected["real_orders_enabled"] is False
    assert selected["readiness"] in {"not_ready", "planned"}
    assert _is_safe({"plans": plans, "selected": selected})


def test_credential_isolation_plan_does_not_read_or_expose_credentials():
    from sandbox.credential_isolation_plan import build_credential_isolation_plan

    plan = build_credential_isolation_plan()

    assert plan["credential_ready"] is False
    assert plan["current_credentials_loaded"] is False
    assert plan["plaintext_secret_allowed"] is False
    assert plan["frontend_secret_exposure_allowed"] is False
    assert plan["future_vault_required"] is True
    assert plan["missing_requirements"]
    assert _is_safe(plan)


def test_sandbox_order_lifecycle_plan_rejects_order_release():
    from sandbox.sandbox_order_lifecycle_plan import build_sandbox_order_lifecycle_plan

    lifecycle = build_sandbox_order_lifecycle_plan()

    assert len(lifecycle["stages"]) == 9
    assert lifecycle["sandbox_order_submission_enabled"] is False
    assert lifecycle["order_release_policy"] in {"rejected", "planned_only"}
    assert lifecycle["real_broker_order"] is None
    assert lifecycle["sandbox_order"] is None
    assert lifecycle["broker_connected"] is False
    assert _is_safe(lifecycle)


def test_sandbox_safety_checklist_is_not_ready_for_connection_or_orders():
    from sandbox.sandbox_safety_checklist import build_sandbox_safety_checklist

    checklist = build_sandbox_safety_checklist()

    assert checklist["ready_for_sandbox_connection"] is False
    assert checklist["ready_for_sandbox_orders"] is False
    assert checklist["checks"]
    assert checklist["blocking_items"]
    assert checklist["paper_trading"] is True
    assert checklist["planning_only"] is True
    assert _is_safe(checklist)


def test_sandbox_rollback_plan_is_planning_only():
    from sandbox.sandbox_rollback_plan import build_sandbox_rollback_plan

    rollback = build_sandbox_rollback_plan()

    assert "disable sandbox connection" in rollback["steps"]
    assert "disable sandbox order submission" in rollback["steps"]
    assert rollback["executes_broker_cancel"] is False
    assert rollback["external_notification_enabled"] is False
    assert rollback["log_upload_enabled"] is False
    assert rollback["planning_only"] is True
    assert _is_safe(rollback)


def test_sandbox_api_endpoints_return_safe_planning_payloads():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/sandbox/status",
        "/api/v5/sandbox/provider-plan",
        "/api/v5/sandbox/credential-policy",
        "/api/v5/sandbox/order-lifecycle",
        "/api/v5/sandbox/safety-checklist",
        "/api/v5/sandbox/rollback-plan",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()

        assert response.status_code == 200
        assert payload["success"] is True
        encoded = json.dumps(payload).lower()
        assert "sandbox_connection_enabled" in encoded
        assert "sandbox_orders_enabled" in encoded
        assert "broker_connected" in encoded
        assert "real_orders_enabled" in encoded
        assert "real_money_enabled" in encoded
        assert "paper_trading" in encoded
        assert "planning_only" in encoded
        assert _is_safe(payload)


def test_sandbox_readiness_report_and_cli_can_run():
    from sandbox.sandbox_readiness_report import generate_sandbox_readiness_report

    result = generate_sandbox_readiness_report()
    assert result["path"].endswith("reports/v5_10_broker_sandbox_readiness_report.md")
    assert result["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(result)

    completed = subprocess.run(
        [sys.executable, "scripts/run_v510_broker_sandbox_readiness.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode in {0, 1}
    payload = json.loads(completed.stdout)
    assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(payload)


def test_v510_frontend_helpers_navigation_docs_and_review_exist():
    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-sandbox/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5SandboxStatus" in api_client
    assert "fetchV5SandboxProviderPlan" in api_client
    assert "fetchV5SandboxCredentialPolicy" in api_client
    assert "fetchV5SandboxOrderLifecycle" in api_client
    assert "fetchV5SandboxSafetyChecklist" in api_client
    assert "fetchV5SandboxRollbackPlan" in api_client
    assert "Sandbox Readiness Status" in page
    assert "Sandbox connection: disabled" in page
    assert "Sandbox orders: disabled" in page
    assert "Broker connected: false" in page
    assert "Real orders: disabled" in page
    assert "Real money: disabled" in page
    assert "Paper trading only" in page
    assert "Planning only" in page
    assert "V5 Sandbox" in shell
    assert "/v5-sandbox" in shell
    assert "V5.10" in _read("docs/V5_BROKER_SANDBOX_READINESS.md")
    assert "V5.10" in _read("README.md")
    assert "V5.10" in _read("REVIEW_PACKAGE.md")
    assert _is_safe(page)


def test_existing_v5_stack_tests_are_available():
    assert "test_paper_trading_runner_completes_closed_loop" in _read("tests/test_v50_paper_trading_core.py")
    assert "test_runtime_loop_runs_and_updates_portfolio" in _read("tests/test_v51_trading_engine_runtime.py")
    assert "test_engine_crash_recovery_logs_error" in _read("tests/test_v52_production_stability_engineering.py")
    assert "soak" in _read("tests/test_v53_long_run_soak_test.py").lower()
    assert "monitoring" in _read("tests/test_v54_live_paper_trading_monitoring_api.py").lower()
    assert "deployment" in _read("tests/test_v55_production_deployment_dry_run.py").lower()
    assert "live paper" in _read("tests/test_v56_live_paper_trading_staging.py").lower()
    assert "live alpha" in _read("tests/test_v57_live_alpha_signal_integration.py").lower()
    assert "broker integration" in _read("tests/test_v58_broker_integration_planning.py").lower()
    assert "manual approval" in _read("tests/test_v59_manual_approval_gate.py").lower()


def test_no_real_sandbox_sdk_or_order_routing_is_introduced():
    planned_files = [
        "config/v5_broker_sandbox_config.py",
        "sandbox/sandbox_provider_plan.py",
        "sandbox/credential_isolation_plan.py",
        "sandbox/sandbox_order_lifecycle_plan.py",
        "sandbox/sandbox_safety_checklist.py",
        "sandbox/sandbox_rollback_plan.py",
        "sandbox/sandbox_readiness_report.py",
    ]
    forbidden = ["alpaca_trade_api", "ib_insync", "tigeropen", "robin_stocks", "place_order", "live_order", "sandbox.submit"]
    for path in planned_files:
        text = _read(path).lower()
        assert not any(term in text for term in forbidden)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _is_safe(payload) -> bool:
    encoded = json.dumps(payload, default=str).lower()
    allowed_policy_terms = [
        "plaintext_secret_allowed",
        "frontend_secret_exposure_allowed",
        "credentials_must_not_be_stored_plaintext",
        "credentials_must_not_be_logged",
        "frontend_never_receives_credentials",
    ]
    for term in allowed_policy_terms:
        encoded = encoded.replace(term, "")
    return not any(term in encoded for term in SENSITIVE_TERMS)

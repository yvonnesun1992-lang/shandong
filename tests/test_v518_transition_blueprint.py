from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


BOUNDARY_FALSE_KEYS = [
    "transition_enabled",
    "sandbox_api_enabled",
    "broker_connected",
    "real_orders_enabled",
    "real_money_enabled",
]


def test_transition_config_defaults_are_blueprint_only():
    from config.v5_transition_blueprint_config import get_transition_blueprint_mode, get_transition_status, get_transition_target_provider

    assert get_transition_blueprint_mode() == "blueprint_only"
    assert get_transition_target_provider() == "none"
    status = get_transition_status()

    assert status["blueprint_only"] is True
    assert status["paper_trading"] is True
    for key in BOUNDARY_FALSE_KEYS:
        assert status[key] is False
    assert _is_safe(status)


def test_blueprints_are_disabled_for_real_transition_paths():
    from transition.credential_vault_blueprint import build_credential_vault_blueprint, validate_no_credentials_present
    from transition.environment_separation_blueprint import build_environment_separation_blueprint
    from transition.feature_flag_blueprint import build_feature_flag_blueprint, validate_feature_flags
    from transition.real_order_blocker_policy import build_real_order_blocker_policy, evaluate_real_order_attempt
    from transition.transition_readiness_blueprint import build_transition_readiness_blueprint

    readiness = build_transition_readiness_blueprint()
    vault = build_credential_vault_blueprint()
    environments = build_environment_separation_blueprint()
    flags = build_feature_flag_blueprint()
    flag_validation = validate_feature_flags(flags["flags"])
    blocker = build_real_order_blocker_policy()
    attempt = evaluate_real_order_attempt({"manual_approval_passed": True, "real_order_requested": True})

    assert len(readiness["sections"]) == 9
    assert all(section["ready"] is False for section in readiness["sections"])
    assert vault["future_vault_required"] is True
    assert validate_no_credentials_present({"payload": "safe blueprint"})["valid"] is True
    assert validate_no_credentials_present({"payload": "api_key=demo"})["valid"] is False
    assert all(env["broker_connection_allowed"] is False for env in environments["environments"])
    assert all(env["real_orders_allowed"] is False for env in environments["environments"])
    assert flags["flags"]["REQUIRE_MANUAL_APPROVAL"] is True
    assert flags["flags"]["ENABLE_KILL_SWITCH"] is True
    assert flags["flags"]["ENABLE_AUDIT_LOGGING"] is True
    assert flags["flags"]["ENABLE_REAL_MONEY"] is False
    assert flag_validation["valid"] is True
    assert blocker["blocked"] is True
    assert attempt["blocked"] is True
    assert attempt["real_order_submitted"] is False
    assert _is_safe({"readiness": readiness, "vault": vault, "environments": environments, "flags": flags, "attempt": attempt})


def test_checklist_kill_switch_rollback_and_safety_validator():
    from transition.kill_switch_blueprint import build_kill_switch_blueprint
    from transition.rollback_blueprint import build_rollback_blueprint
    from transition.sandbox_enablement_checklist import build_sandbox_enablement_checklist
    from transition.transition_safety_validator import build_transition_safety_summary, validate_no_real_connection, validate_no_real_order_path

    checklist = build_sandbox_enablement_checklist()
    kill_switch = build_kill_switch_blueprint()
    rollback = build_rollback_blueprint()
    safety = build_transition_safety_summary()

    assert checklist["ready_to_enable_sandbox_api"] is False
    assert checklist["ready_to_submit_sandbox_orders"] is False
    assert len(checklist["checklist"]) >= 10
    assert "global kill switch" in kill_switch["controls"]
    assert "switch to paper-only" in rollback["steps"]
    assert validate_no_real_connection()["safe"] is True
    assert validate_no_real_order_path()["safe"] is True
    assert safety["safe"] is True
    assert safety["blueprint_only"] is True
    assert _is_safe({"checklist": checklist, "kill_switch": kill_switch, "rollback": rollback, "safety": safety})


def test_transition_api_endpoints_return_safe_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/transition/status",
        "/api/v5/transition/readiness",
        "/api/v5/transition/credential-vault",
        "/api/v5/transition/environments",
        "/api/v5/transition/feature-flags",
        "/api/v5/transition/sandbox-checklist",
        "/api/v5/transition/real-order-blocker",
        "/api/v5/transition/kill-switch",
        "/api/v5/transition/rollback",
        "/api/v5/transition/safety",
    ]

    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "blueprint_only" in encoded
        assert "paper_trading" in encoded
        for key in BOUNDARY_FALSE_KEYS:
            assert key in encoded
        assert _is_safe(payload)


def test_transition_report_cli_frontend_docs_and_navigation_are_present():
    from transition.transition_blueprint_report import generate_transition_blueprint_report

    report = generate_transition_blueprint_report("safety")
    assert report["path"].endswith("reports/v5_18_transition_blueprint_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["summary"]["blueprint_only"] is True

    for args in [[], ["--check", "safety"], ["--check", "sandbox-checklist"], ["--check", "real-order-blocker"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v518_transition_blueprint.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["blueprint_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-transition/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    for name in [
        "fetchV5TransitionStatus",
        "fetchV5TransitionReadiness",
        "fetchV5TransitionCredentialVault",
        "fetchV5TransitionEnvironments",
        "fetchV5TransitionFeatureFlags",
        "fetchV5TransitionSandboxChecklist",
        "fetchV5TransitionRealOrderBlocker",
        "fetchV5TransitionKillSwitch",
        "fetchV5TransitionRollback",
        "fetchV5TransitionSafety",
    ]:
        assert name in api_client
    for label in [
        "Transition Status",
        "Readiness Blueprint",
        "Credential Vault Blueprint",
        "Environment Separation",
        "Feature Flags",
        "Sandbox Enablement Checklist",
        "Real Order Blocker",
        "Kill Switch Blueprint",
        "Rollback Blueprint",
        "Safety Validation",
    ]:
        assert label in page
    assert "blueprint only" in page.lower()
    assert "transition disabled" in page.lower()
    assert "sandbox api disabled" in page.lower()
    assert "broker connected false" in page.lower()
    assert "real orders disabled" in page.lower()
    assert "real money disabled" in page.lower()
    assert "paper trading only" in page.lower()
    assert "V5 Transition" in shell
    assert "/v5-transition" in shell
    assert "V5.18" in _read("docs/V5_TRANSITION_BLUEPRINT.md")
    assert "V5.18" in _read("README.md")
    assert "V5.18" in _read("REVIEW_PACKAGE.md")
    assert "scan_transition_blueprint_outputs" in _read("runtime/security_scan.py")
    assert _is_safe(page)


def test_no_sdk_network_or_real_runtime_strings_in_transition_modules():
    planned_files = [
        "transition/transition_readiness_blueprint.py",
        "transition/credential_vault_blueprint.py",
        "transition/environment_separation_blueprint.py",
        "transition/feature_flag_blueprint.py",
        "transition/sandbox_enablement_checklist.py",
        "transition/real_order_blocker_policy.py",
        "transition/kill_switch_blueprint.py",
        "transition/rollback_blueprint.py",
        "transition/transition_safety_validator.py",
        "transition/transition_blueprint_report.py",
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


def test_existing_v5_stack_tests_are_available_through_v517():
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
        "sandbox broker credential",
    ]
    return not any(term in text for term in blocked)

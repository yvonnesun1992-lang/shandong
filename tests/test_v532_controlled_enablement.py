from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "controlled_enablement_runtime_enabled",
    "controlled_go_enabled",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "order_preview_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_controlled_enablement_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_controlled_enablement_config import (
        get_controlled_enablement_mode,
        get_controlled_enablement_provider,
        get_controlled_enablement_status,
    )

    assert get_controlled_enablement_mode() == "controlled_blueprint_only"
    assert get_controlled_enablement_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_controlled_enablement_status()
    assert status["version"] == "V5.32"
    assert status["controlled_blueprint_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    for env_name in [
        "SHANDONG_V5_ENABLE_CONTROLLED_RUNTIME",
        "SHANDONG_V5_ENABLE_CONTROLLED_GO",
        "SHANDONG_V5_ENABLE_SANDBOX_API",
        "SHANDONG_V5_ENABLE_SECRET_READ",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ",
        "SHANDONG_V5_ENABLE_ORDER_PREVIEW",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION",
        "SHANDONG_V5_ENABLE_REAL_MONEY",
    ]:
        monkeypatch.setenv(env_name, "true")
    blocked = get_controlled_enablement_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "controlled runtime requested but blocked in v5.32" in warnings
    assert "controlled go requested but blocked in v5.32" in warnings
    assert "sandbox api requested but blocked in v5.32" in warnings
    assert "secret read requested but blocked in v5.32" in warnings
    assert "account read requested but blocked in v5.32" in warnings
    assert "order preview requested but blocked in v5.32" in warnings
    assert "order submission requested but blocked in v5.32" in warnings
    assert "real money requested but blocked in v5.32" in warnings
    assert _is_safe(blocked)


def test_controlled_enablement_components_decision_safety_and_orchestrator():
    from sandbox_controlled_enablement.account_read_enablement_conditions import build_account_read_enablement_conditions
    from sandbox_controlled_enablement.controlled_enablement_conditions import build_controlled_enablement_conditions
    from sandbox_controlled_enablement.controlled_enablement_decision_record import (
        build_controlled_enablement_decision,
        evaluate_controlled_enablement_decision,
    )
    from sandbox_controlled_enablement.controlled_enablement_orchestrator import (
        build_controlled_enablement_blueprint,
        summarize_controlled_enablement_blueprint,
    )
    from sandbox_controlled_enablement.controlled_enablement_safety_validator import (
        build_controlled_enablement_safety_summary,
        validate_controlled_enablement_safety,
    )
    from sandbox_controlled_enablement.emergency_stop_conditions import build_emergency_stop_conditions
    from sandbox_controlled_enablement.feature_flag_dependency_graph import build_feature_flag_dependency_graph
    from sandbox_controlled_enablement.order_preview_enablement_conditions import build_order_preview_enablement_conditions
    from sandbox_controlled_enablement.order_submission_blocker import (
        build_order_submission_blocker,
        evaluate_order_submission_attempt,
    )
    from sandbox_controlled_enablement.sandbox_api_enablement_conditions import build_sandbox_api_enablement_conditions
    from sandbox_controlled_enablement.secret_read_enablement_conditions import build_secret_read_enablement_conditions
    from sandbox_controlled_enablement.staged_unlock_plan import build_staged_unlock_plan

    conditions = build_controlled_enablement_conditions("alpaca")
    stages = build_staged_unlock_plan("alpaca")
    flags = build_feature_flag_dependency_graph("alpaca")
    secret = build_secret_read_enablement_conditions("alpaca")
    sandbox_api = build_sandbox_api_enablement_conditions("alpaca")
    account = build_account_read_enablement_conditions("alpaca")
    preview = build_order_preview_enablement_conditions("alpaca")
    blocker = build_order_submission_blocker("alpaca")
    attempted = evaluate_order_submission_attempt({"provider": "alpaca", "manual_approval": True, "controlled_go": True})
    emergency = build_emergency_stop_conditions("alpaca")
    decision = build_controlled_enablement_decision("alpaca")
    simulated = evaluate_controlled_enablement_decision({"provider": "alpaca", "controlled_go_requested": True, "simulated_approval": True})
    safety = build_controlled_enablement_safety_summary()
    blueprint = build_controlled_enablement_blueprint("alpaca")
    summary = summarize_controlled_enablement_blueprint(blueprint)

    assert conditions["conditions_met"] is False
    assert "credential vault live and tested" in [item["name"] for item in conditions["controlled_go_conditions"]]
    assert conditions["blocking_items"]
    assert stages["stages"]
    assert all(stage["enabled"] is False and stage["executable_now"] is False for stage in stages["stages"])
    assert [stage for stage in stages["stages"] if stage["stage"] == "stage_8_sandbox_order_submission_future_blocked"][0]["blocked"] is True
    assert "ORDER_SUBMISSION" in flags["dependency_graph"]
    assert flags["dependency_graph"]["ORDER_SUBMISSION"]["blocked"] is True
    assert flags["dependency_graph"]["REAL_MONEY"]["blocked"] is True
    assert flags["current_flags"]["CONTROLLED_GO"] is False
    assert flags["invalid_unlock_paths"]
    assert secret["secret_read_ready"] is False and secret["secret_read_enabled"] is False
    assert sandbox_api["sandbox_api_ready"] is False and sandbox_api["sandbox_api_enabled"] is False
    assert account["account_read_ready"] is False and account["account_read_enabled"] is False
    assert preview["order_preview_ready"] is False
    assert preview["order_preview_enabled"] is False
    assert preview["order_submission_enabled"] is False
    assert blocker["blocked"] is True
    assert blocker["sandbox_order_submission_allowed"] is False
    assert blocker["real_order_submission_allowed"] is False
    assert attempted["blocked"] is True
    assert attempted["sandbox_order_submission_allowed"] is False
    assert attempted["real_order_submission_allowed"] is False
    assert emergency["emergency_stop_conditions"]
    assert emergency["emergency_stop_ready"] is False
    assert emergency["current_action"] == "NO_RUNTIME_TO_STOP"
    assert decision["decision"] == "CONTROLLED_GO_BLOCKED"
    assert simulated["decision"] == "CONTROLLED_GO_BLOCKED"
    for key in FALSE_KEYS:
        assert decision[key] is False
        assert simulated[key] is False
    assert safety["safe"] is True
    for key in FALSE_KEYS:
        assert validate_controlled_enablement_safety({key: True})["safe"] is False
    assert validate_controlled_enablement_safety({"payload": "secret_value=demo"})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert summary["controlled_go_enabled"] is False
    for item in [conditions, stages, flags, secret, sandbox_api, account, preview, blocker, attempted, emergency, decision, simulated, safety, summary]:
        assert item["controlled_blueprint_only"] is True
        assert _is_safe(item)


def test_controlled_enablement_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/controlled-enablement/status",
        "/api/v5/controlled-enablement/conditions",
        "/api/v5/controlled-enablement/stages",
        "/api/v5/controlled-enablement/feature-flags",
        "/api/v5/controlled-enablement/secret-read",
        "/api/v5/controlled-enablement/sandbox-api",
        "/api/v5/controlled-enablement/account-read",
        "/api/v5/controlled-enablement/order-preview",
        "/api/v5/controlled-enablement/order-submission-blocker",
        "/api/v5/controlled-enablement/emergency-stop",
        "/api/v5/controlled-enablement/decision",
        "/api/v5/controlled-enablement/safety",
        "/api/v5/controlled-enablement/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "controlled_blueprint_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from runtime.security_scan import scan_controlled_enablement_outputs
    from sandbox_controlled_enablement.sandbox_controlled_enablement_report import generate_sandbox_controlled_enablement_report

    report = generate_sandbox_controlled_enablement_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_32_sandbox_controlled_enablement_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["controlled_blueprint_only"] is True
    assert scan_controlled_enablement_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "conditions"], ["--check", "feature-flags"], ["--check", "decision"], ["--check", "safety"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v532_controlled_enablement.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["controlled_blueprint_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-controlled-enablement/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_CONTROLLED_ENABLEMENT_BLUEPRINT.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5ControlledEnablementStatus",
        "fetchV5ControlledEnablementConditions",
        "fetchV5ControlledEnablementStages",
        "fetchV5ControlledEnablementFeatureFlags",
        "fetchV5ControlledEnablementCredentialRead",
        "fetchV5ControlledEnablementSandboxApi",
        "fetchV5ControlledEnablementAccountRead",
        "fetchV5ControlledEnablementOrderPreview",
        "fetchV5ControlledEnablementOrderSubmissionBlocker",
        "fetchV5ControlledEnablementEmergencyStop",
        "fetchV5ControlledEnablementDecision",
        "fetchV5ControlledEnablementSafety",
        "fetchV5ControlledEnablementSummary",
    ]:
        assert name in api_client
    assert "V5 Controlled Enablement" in shell
    assert "Controlled Enablement" in page
    assert "CONTROLLED_GO_BLOCKED" in page
    assert "V5.32 Sandbox Dry-Run Controlled Enablement Blueprint" in docs
    assert "scan_controlled_enablement_outputs" in scanner


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _is_safe(payload: object) -> bool:
    text = json.dumps(payload, default=str).lower()
    blocked = [
        "api_key=demo",
        "secret_value=demo",
        "token=demo",
        "password=demo",
        "authorization",
        "real_order_id",
        "account_id",
        "raw provider response",
        "provider_endpoint_url",
        "controlled_go_enabled\": true",
        "sandbox_api_enabled\": true",
        "secret_read_enabled\": true",
        "account_read_enabled\": true",
        "order_preview_enabled\": true",
        "order_submission_enabled\": true",
        "broker_connected\": true",
        "real_money_enabled\": true",
        "paper-api.",
        "api.alpaca.",
    ]
    return not any(term in text for term in blocked)

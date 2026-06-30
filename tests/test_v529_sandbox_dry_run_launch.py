from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "launch_runtime_enabled",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_dry_run_launch_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_sandbox_dry_run_launch_config import (
        get_dry_run_launch_mode,
        get_dry_run_launch_provider,
        get_dry_run_launch_status,
    )

    assert get_dry_run_launch_mode() == "launch_plan_only"
    assert get_dry_run_launch_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_dry_run_launch_status()
    assert status["version"] == "V5.29"
    assert status["launch_plan_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_DRY_RUN_RUNTIME", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SECRET_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ACCOUNT_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_dry_run_launch_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "dry-run runtime requested but blocked in v5.29" in warnings
    assert "sandbox api requested but blocked in v5.29" in warnings
    assert "secret read requested but blocked in v5.29" in warnings
    assert "account read requested but blocked in v5.29" in warnings
    assert "order submission requested but blocked in v5.29" in warnings
    assert "real money requested but blocked in v5.29" in warnings
    assert _is_safe(blocked)


def test_launch_plan_components_gate_safety_and_orchestrator():
    from sandbox_dry_run_launch.dry_run_rollback_plan import build_dry_run_rollback_plan
    from sandbox_dry_run_launch.dry_run_scope_definition import build_dry_run_scope_definition
    from sandbox_dry_run_launch.dry_run_launch_orchestrator import build_dry_run_launch_plan, summarize_dry_run_launch_plan
    from sandbox_dry_run_launch.feature_flag_launch_plan import build_feature_flag_launch_plan, validate_feature_flag_plan
    from sandbox_dry_run_launch.go_no_go_gate import build_go_no_go_summary, evaluate_go_no_go_gate
    from sandbox_dry_run_launch.launch_audit_trail import build_launch_audit_event, build_launch_audit_trail
    from sandbox_dry_run_launch.launch_safety_validator import build_launch_safety_summary, validate_launch_safety
    from sandbox_dry_run_launch.launch_sequence_plan import build_launch_sequence_plan
    from sandbox_dry_run_launch.preflight_checklist import build_preflight_checklist
    from sandbox_dry_run_launch.responsibility_matrix import build_responsibility_matrix

    scope = build_dry_run_scope_definition("alpaca")
    flags = build_feature_flag_launch_plan("alpaca")
    responsibilities = build_responsibility_matrix("alpaca")
    preflight = build_preflight_checklist("alpaca")
    sequence = build_launch_sequence_plan("alpaca")
    rollback = build_dry_run_rollback_plan("alpaca")
    gate = evaluate_go_no_go_gate("alpaca")
    gate_summary = build_go_no_go_summary("alpaca")
    audit_event = build_launch_audit_event("alpaca", "simulate_start")
    audit_trail = build_launch_audit_trail("alpaca")
    safety = build_launch_safety_summary()
    plan = build_dry_run_launch_plan("alpaca")
    summary = summarize_dry_run_launch_plan(plan)

    assert scope["dry_run_scope"]["dry_run_type"] == "read_only_first"
    assert scope["ready"] is False
    assert flags["flags"]["ENABLE_SANDBOX_API"] is False
    assert flags["flags"]["ENABLE_ORDER_SUBMISSION"] is False
    assert validate_feature_flag_plan({"ENABLE_SANDBOX_API": True})["valid"] is False
    assert validate_feature_flag_plan({"ENABLE_SECRET_READ": True})["valid"] is False
    assert validate_feature_flag_plan({"ENABLE_ORDER_SUBMISSION": True})["valid"] is False
    assert responsibilities["roles"]["vault_operator"]["can_read_secret"] is False
    assert responsibilities["roles"]["technical_operator"]["can_enable_flags"] is False
    assert responsibilities["roles"]["risk_operator"]["can_submit_order"] is False
    assert preflight["preflight_ready"] is False
    assert "sandbox api disabled" in " ".join(preflight["blocking_items"]).lower()
    assert all(step["execution"] == "simulate_only" for step in sequence["steps"])
    assert rollback["all_real_paths_disabled"] is True
    assert gate["gate"] == "NO_GO"
    assert gate["dry_run_launch_allowed"] is False
    assert gate_summary["gate"] == "NO_GO"
    assert audit_event["launch_audit_id_placeholder"] == "LAUNCH_AUDIT_PLACEHOLDER"
    assert audit_event["raw_secret_logged"] is False
    assert audit_event["order_submitted"] is False
    assert audit_event["account_read"] is False
    assert audit_trail["external_log_upload"] is False
    assert safety["safe"] is True
    assert validate_launch_safety({"launch_runtime_enabled": True})["safe"] is False
    assert validate_launch_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_launch_safety({"secret_read_enabled": True})["safe"] is False
    assert validate_launch_safety({"account_read_enabled": True})["safe"] is False
    assert validate_launch_safety({"order_submission_enabled": True})["safe"] is False
    assert validate_launch_safety({"payload": "api_key=demo"})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    for item in [scope, flags, responsibilities, preflight, sequence, rollback, gate, audit_event, audit_trail, safety, summary]:
        assert item["launch_plan_only"] is True
        assert _is_safe(item)


def test_sandbox_dry_run_launch_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/sandbox-dry-run-launch/status",
        "/api/v5/sandbox-dry-run-launch/scope",
        "/api/v5/sandbox-dry-run-launch/feature-flags",
        "/api/v5/sandbox-dry-run-launch/responsibility",
        "/api/v5/sandbox-dry-run-launch/preflight",
        "/api/v5/sandbox-dry-run-launch/sequence",
        "/api/v5/sandbox-dry-run-launch/rollback",
        "/api/v5/sandbox-dry-run-launch/gate",
        "/api/v5/sandbox-dry-run-launch/audit",
        "/api/v5/sandbox-dry-run-launch/safety",
        "/api/v5/sandbox-dry-run-launch/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "launch_plan_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from runtime.security_scan import scan_sandbox_dry_run_launch_outputs
    from sandbox_dry_run_launch.sandbox_dry_run_launch_report import generate_sandbox_dry_run_launch_report

    report = generate_sandbox_dry_run_launch_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_29_sandbox_dry_run_launch_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["launch_plan_only"] is True
    assert scan_sandbox_dry_run_launch_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "preflight"], ["--check", "gate"], ["--check", "safety"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v529_sandbox_dry_run_launch.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["launch_plan_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-sandbox-dry-run-launch/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_SANDBOX_DRY_RUN_LAUNCH.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5SandboxDryRunLaunchStatus",
        "fetchV5SandboxDryRunLaunchScope",
        "fetchV5SandboxDryRunLaunchFeatureFlags",
        "fetchV5SandboxDryRunLaunchResponsibility",
        "fetchV5SandboxDryRunLaunchPreflight",
        "fetchV5SandboxDryRunLaunchSequence",
        "fetchV5SandboxDryRunLaunchRollback",
        "fetchV5SandboxDryRunLaunchGate",
        "fetchV5SandboxDryRunLaunchAudit",
        "fetchV5SandboxDryRunLaunchSafety",
        "fetchV5SandboxDryRunLaunchSummary",
    ]:
        assert name in api_client
    assert "V5 Dry-Run Launch" in shell
    assert "Sandbox Dry-Run Launch" in page
    assert "Go / No-Go Gate" in page
    assert "V5.29 Sandbox Dry-Run Launch Plan" in docs
    assert "scan_sandbox_dry_run_launch_outputs" in scanner


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
        "sandbox_api_enabled\": true",
        "secret_read_enabled\": true",
        "account_read_enabled\": true",
        "order_submission_enabled\": true",
        "broker_connected\": true",
        "real_money_enabled\": true",
        "paper-api.",
        "api.alpaca.",
    ]
    return not any(term in text for term in blocked)

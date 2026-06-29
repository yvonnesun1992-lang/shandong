from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}
FAULT_SCENARIOS = {
    "connector_timeout",
    "provider_reject",
    "duplicate_order",
    "stale_response",
    "out_of_order_event",
    "partial_fill_mismatch",
    "rate_limit_storm",
    "audit_loss",
    "state_machine_corruption",
    "recovery_rollback",
    "kill_switch_trigger",
    "idempotency_collision",
}
FALSE_KEYS = [
    "fault_injection_runtime_enabled",
    "sandbox_api_enabled",
    "account_read_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_fault_injection_config_defaults_and_blocks_real_path_env(monkeypatch):
    from config.v5_provider_fault_injection_config import (
        get_fault_injection_mode,
        get_fault_injection_provider,
        get_fault_injection_status,
    )

    assert get_fault_injection_mode() == "fault_injection_only"
    assert get_fault_injection_provider() in PROVIDERS
    status = get_fault_injection_status()
    assert status["version"] == "V5.24"
    assert status["fault_injection_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_FAULT_INJECTION_RUNTIME", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ACCOUNT_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_fault_injection_status()

    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "fault injection runtime requested but blocked in v5.24" in warnings
    assert "sandbox api requested but blocked in v5.24" in warnings
    assert "account read requested but blocked in v5.24" in warnings
    assert "order submission requested but blocked in v5.24" in warnings
    assert "real money requested but blocked in v5.24" in warnings
    assert _is_safe(blocked)


def test_fault_scenario_catalog_and_injector_are_placeholder_only():
    from provider_fault_injection.fault_injector import inject_all_faults, inject_fault
    from provider_fault_injection.fault_scenario_catalog import build_fault_scenario_catalog

    catalog = build_fault_scenario_catalog("alpaca")
    single = inject_fault("alpaca", "connector_timeout")
    all_faults = inject_all_faults("alpaca")

    assert catalog["provider"] == "alpaca"
    assert set(catalog["scenarios"]) >= FAULT_SCENARIOS
    assert single["scenario"] == "connector_timeout"
    assert single["injected"] is True
    assert single["fault_injection_only"] is True
    assert "FAULT_INJECTED" in [event["event_type"] for event in single["events"]]
    assert all_faults["total_scenarios"] >= len(FAULT_SCENARIOS)
    assert all(result["injected"] for result in all_faults["results"])
    assert _is_safe(catalog)
    assert _is_safe(single)


def test_fault_replay_runner_detects_recovers_and_keeps_orders_disabled():
    from provider_fault_injection.fault_replay_runner import (
        run_all_fault_scenarios,
        run_fault_scenario,
    )

    timeout = run_fault_scenario("alpaca", "connector_timeout")
    collision = run_fault_scenario("alpaca", "idempotency_collision")
    all_results = run_all_fault_scenarios("alpaca")

    assert timeout["scenario"] == "connector_timeout"
    assert timeout["detected"] is True
    assert timeout["recovered"] is True
    assert timeout["audit_written"] is True
    assert timeout["final_state"] in {"SAFE_RECOVERED", "KILL_SWITCH_SIMULATED"}
    assert collision["scenario"] == "idempotency_collision"
    assert collision["detected"] is True
    assert collision["recovered"] is True
    assert all_results["total_scenarios"] >= len(FAULT_SCENARIOS)
    assert all(result["order_submission_enabled"] is False for result in all_results["results"])
    assert all(result["sandbox_api_enabled"] is False for result in all_results["results"])
    assert _is_safe(timeout)
    assert _is_safe(collision)


def test_detection_recovery_kill_switch_audit_safety_and_orchestrator_pass_or_warn():
    from provider_fault_injection.fault_audit_trail import build_all_fault_audit_trails
    from provider_fault_injection.fault_detection_validator import validate_all_fault_detections
    from provider_fault_injection.fault_injection_orchestrator import run_fault_injection_suite
    from provider_fault_injection.fault_recovery_validator import validate_all_fault_recovery
    from provider_fault_injection.fault_safety_validator import (
        build_fault_safety_summary,
        validate_fault_safety,
    )
    from provider_fault_injection.kill_switch_simulation import (
        simulate_kill_switch_trigger,
        validate_kill_switch_effect,
    )

    detection = validate_all_fault_detections("alpaca")
    recovery = validate_all_fault_recovery("alpaca")
    kill_switch = simulate_kill_switch_trigger("alpaca", "kill_switch_trigger")
    kill_switch_validation = validate_kill_switch_effect(kill_switch)
    audit = build_all_fault_audit_trails("alpaca")
    safety = build_fault_safety_summary()
    summary = run_fault_injection_suite("alpaca")

    assert detection["valid"] is True
    assert set(detection["detected_faults"]) >= {
        "connector_timeout",
        "duplicate_order",
        "stale_response",
        "out_of_order_event",
        "partial_fill_mismatch",
        "rate_limit_storm",
        "audit_loss",
        "state_machine_corruption",
        "idempotency_collision",
    }
    assert recovery["valid"] is True
    assert kill_switch["kill_switch_triggered"] is True
    assert kill_switch["order_submission_enabled"] is False
    assert kill_switch["sandbox_api_enabled"] is False
    assert kill_switch_validation["valid"] is True
    assert audit["valid"] is True
    first_audit = audit["audit_trails"][0]["audit_events"][0]
    assert first_audit["audit_event_id_placeholder"].startswith("FAULT_AUDIT_EVENT_ID_PLACEHOLDER")
    assert first_audit["actor"] == "offline_fault_injection_suite"
    assert first_audit["raw_payload_stored"] is False
    assert first_audit["provider_payload_redacted"] is True
    assert safety["safe"] is True
    assert validate_fault_safety({"fault_injection_runtime_enabled": True})["safe"] is False
    assert validate_fault_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_fault_safety({"account_read_enabled": True})["safe"] is False
    assert validate_fault_safety({"order_submission_enabled": True})["safe"] is False
    assert validate_fault_safety({"payload": "token=demo"})["safe"] is False
    assert validate_fault_safety({"payload": "raw provider payload"})["safe"] is False
    assert validate_fault_safety({"payload": "https://paper-api.alpaca.markets"})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert summary["failed"] == 0
    assert summary["fault_injection_only"] is True
    for item in [detection, recovery, kill_switch, kill_switch_validation, audit, safety, summary]:
        assert _is_safe(item)


def test_provider_fault_injection_api_endpoints_return_safe_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/provider-fault-injection/status",
        "/api/v5/provider-fault-injection/scenarios",
        "/api/v5/provider-fault-injection/inject",
        "/api/v5/provider-fault-injection/run",
        "/api/v5/provider-fault-injection/detection",
        "/api/v5/provider-fault-injection/recovery",
        "/api/v5/provider-fault-injection/kill-switch",
        "/api/v5/provider-fault-injection/audit",
        "/api/v5/provider-fault-injection/safety",
        "/api/v5/provider-fault-injection/summary",
    ]

    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "fault_injection_only" in encoded
        assert "paper_trading" in encoded
        for key in FALSE_KEYS:
            assert key in encoded
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from provider_fault_injection.provider_fault_injection_report import (
        generate_provider_fault_injection_report,
    )
    from runtime.security_scan import scan_provider_fault_injection_outputs

    report = generate_provider_fault_injection_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_24_provider_fault_injection_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["fault_injection_only"] is True
    assert report["summary"]["provider"] == "alpaca"
    assert scan_provider_fault_injection_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [
        [],
        ["--provider", "alpaca"],
        ["--provider", "ibkr"],
        ["--scenario", "connector_timeout"],
        ["--scenario", "idempotency_collision"],
        ["--check", "safety"],
        ["--check", "recovery"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v524_provider_fault_injection.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["fault_injection_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-provider-fault-injection/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_PROVIDER_FAULT_INJECTION.md")
    scanner = _read("runtime/security_scan.py")

    for name in [
        "fetchV5ProviderFaultInjectionStatus",
        "fetchV5ProviderFaultInjectionScenarios",
        "fetchV5ProviderFaultInjectionInject",
        "fetchV5ProviderFaultInjectionRun",
        "fetchV5ProviderFaultInjectionDetection",
        "fetchV5ProviderFaultInjectionRecovery",
        "fetchV5ProviderFaultInjectionKillSwitch",
        "fetchV5ProviderFaultInjectionAudit",
        "fetchV5ProviderFaultInjectionSafety",
        "fetchV5ProviderFaultInjectionSummary",
    ]:
        assert name in api_client
    for label in [
        "Fault Injection Status",
        "Fault Scenario Catalog",
        "Fault Injector",
        "Fault Replay Runner",
        "Detection Validation",
        "Recovery Validation",
        "Kill Switch Simulation",
        "Fault Audit Trail",
        "Safety Validation",
        "Final Summary",
    ]:
        assert label in page
    assert "V5 Fault Injection" in shell
    assert "V5.24 Provider Sandbox Connector Fault Injection Suite" in docs
    assert "scan_provider_fault_injection_outputs" in scanner


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _is_safe(payload: object) -> bool:
    text = json.dumps(payload, default=str).lower()
    blocked = [
        "provider_endpoint_url",
        "api_key",
        "secret",
        "token=",
        "password",
        "authorization",
        "real_order_id",
        "account_id",
        "raw provider response",
        "sandbox_api_enabled\": true",
        "order_submission_enabled\": true",
        "broker_connected\": true",
        "real_money_enabled\": true",
        "paper-api.",
        "api.alpaca.",
    ]
    return not any(term in text for term in blocked)

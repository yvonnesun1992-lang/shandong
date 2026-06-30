from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}
SCENARIOS = {
    "short_soak_100_events",
    "medium_soak_1000_events",
    "long_soak_5000_events",
    "mixed_replay_fault_soak",
    "duplicate_heavy_soak",
    "rate_limit_heavy_soak",
    "timeout_recovery_soak",
    "audit_heavy_soak",
    "state_machine_boundary_soak",
    "safety_boundary_soak",
}
FALSE_KEYS = [
    "soak_runtime_enabled",
    "sandbox_api_enabled",
    "account_read_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_offline_soak_config_defaults_and_blocks_real_path_env(monkeypatch):
    from config.v5_provider_offline_soak_config import (
        get_offline_soak_mode,
        get_offline_soak_provider,
        get_offline_soak_status,
    )

    assert get_offline_soak_mode() == "offline_soak_only"
    assert get_offline_soak_provider() in PROVIDERS
    status = get_offline_soak_status()
    assert status["version"] == "V5.25"
    assert status["offline_soak_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_OFFLINE_SOAK_RUNTIME", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ACCOUNT_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_offline_soak_status()

    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "offline soak runtime requested but blocked in v5.25" in warnings
    assert "sandbox api requested but blocked in v5.25" in warnings
    assert "account read requested but blocked in v5.25" in warnings
    assert "order submission requested but blocked in v5.25" in warnings
    assert "real money requested but blocked in v5.25" in warnings
    assert _is_safe(blocked)


def test_soak_scenario_plan_and_event_generator_are_deterministic():
    from provider_offline_soak.soak_event_generator import generate_all_soak_events, generate_soak_events
    from provider_offline_soak.soak_scenario_plan import build_soak_scenario_plan

    plan = build_soak_scenario_plan("alpaca")
    first = generate_soak_events("alpaca", "short_soak_100_events")
    second = generate_soak_events("alpaca", "short_soak_100_events")
    all_events = generate_all_soak_events("alpaca")

    assert set(plan["scenarios"]) >= SCENARIOS
    assert first["scenario"] == "short_soak_100_events"
    assert first["event_count"] == 100
    assert first == second
    assert first["offline_soak_only"] is True
    assert all_events["total_scenarios"] >= len(SCENARIOS)
    assert all(result["offline_soak_only"] for result in all_events["results"])
    assert _is_safe(plan)
    assert _is_safe(first)


def test_runner_metrics_gate_coverage_safety_and_orchestrator_pass_or_warn():
    from provider_offline_soak.offline_soak_orchestrator import run_offline_soak, summarize_offline_soak_results
    from provider_offline_soak.soak_coverage_validator import validate_soak_coverage
    from provider_offline_soak.soak_runner import run_all_soak_scenarios, run_soak_scenario
    from provider_offline_soak.soak_safety_validator import build_soak_safety_summary, validate_soak_safety
    from provider_offline_soak.stability_gate import evaluate_all_stability_gates, evaluate_stability_gate
    from provider_offline_soak.stability_metrics import compute_all_stability_metrics, compute_stability_metrics

    short = run_soak_scenario("alpaca", "short_soak_100_events")
    mixed = run_soak_scenario("alpaca", "mixed_replay_fault_soak")
    all_results = run_all_soak_scenarios("alpaca")
    metrics = compute_stability_metrics(short)
    all_metrics = compute_all_stability_metrics("alpaca")
    gate = evaluate_stability_gate(metrics)
    all_gates = evaluate_all_stability_gates("alpaca")
    coverage = validate_soak_coverage("alpaca")
    safety = build_soak_safety_summary()
    orchestrated = run_offline_soak("alpaca")
    summary = summarize_offline_soak_results(orchestrated)

    assert short["processed_events"] == short["event_count"]
    assert short["terminal_state"] == "SOAK_COMPLETED"
    assert mixed["recovery_events_detected"] > 0
    assert all_results["total_scenarios"] >= len(SCENARIOS)
    assert metrics["processed_event_ratio"] == 1.0
    assert metrics["audit_coverage_rate"] >= 0.95
    assert metrics["stability_score"] >= 0.80
    assert all_metrics["total_scenarios"] >= len(SCENARIOS)
    assert gate["gate"] in {"PASS", "WARNING"}
    assert gate["passed"] is True
    assert all_gates["failed"] == 0
    assert coverage["coverage_passed"] is True
    assert safety["safe"] is True
    assert validate_soak_safety({"soak_runtime_enabled": True})["safe"] is False
    assert validate_soak_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_soak_safety({"account_read_enabled": True})["safe"] is False
    assert validate_soak_safety({"order_submission_enabled": True})["safe"] is False
    assert validate_soak_safety({"payload": "token=demo"})["safe"] is False
    assert validate_soak_safety({"payload": "raw provider payload"})["safe"] is False
    assert validate_soak_safety({"payload": "https://paper-api.alpaca.markets"})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert summary["failed"] == 0
    for item in [short, mixed, all_results, metrics, all_metrics, gate, all_gates, coverage, safety, summary]:
        assert item["offline_soak_only"] is True
        assert _is_safe(item)


def test_provider_offline_soak_api_endpoints_return_safe_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/provider-offline-soak/status",
        "/api/v5/provider-offline-soak/plan",
        "/api/v5/provider-offline-soak/generate",
        "/api/v5/provider-offline-soak/run",
        "/api/v5/provider-offline-soak/metrics",
        "/api/v5/provider-offline-soak/gate",
        "/api/v5/provider-offline-soak/coverage",
        "/api/v5/provider-offline-soak/safety",
        "/api/v5/provider-offline-soak/summary",
    ]

    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "offline_soak_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from provider_offline_soak.provider_offline_soak_report import generate_provider_offline_soak_report
    from runtime.security_scan import scan_provider_offline_soak_outputs

    report = generate_provider_offline_soak_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_25_provider_offline_soak_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["offline_soak_only"] is True
    assert report["summary"]["provider"] == "alpaca"
    assert scan_provider_offline_soak_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [
        [],
        ["--provider", "alpaca"],
        ["--provider", "ibkr"],
        ["--scenario", "short_soak_100_events"],
        ["--scenario", "mixed_replay_fault_soak"],
        ["--check", "safety"],
        ["--check", "gate"],
        ["--check", "coverage"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v525_provider_offline_soak.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["offline_soak_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-provider-offline-soak/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_PROVIDER_OFFLINE_SOAK.md")
    scanner = _read("runtime/security_scan.py")

    for name in [
        "fetchV5ProviderOfflineSoakStatus",
        "fetchV5ProviderOfflineSoakPlan",
        "fetchV5ProviderOfflineSoakGenerate",
        "fetchV5ProviderOfflineSoakRun",
        "fetchV5ProviderOfflineSoakMetrics",
        "fetchV5ProviderOfflineSoakGate",
        "fetchV5ProviderOfflineSoakCoverage",
        "fetchV5ProviderOfflineSoakSafety",
        "fetchV5ProviderOfflineSoakSummary",
    ]:
        assert name in api_client
    assert "V5 Offline Soak" in shell
    assert "Offline Soak Status" in page
    assert "Stability Gate" in page
    assert "V5.25 Provider Sandbox Offline Soak" in docs
    assert "scan_provider_offline_soak_outputs" in scanner


def test_all_previous_v5_test_files_exist_through_v524():
    for version in [
        "v50_paper_trading_core",
        "v51_trading_engine_runtime",
        "v52_production_stability_engineering",
        "v53_long_run_soak_test",
        "v54_live_paper_trading_monitoring_api",
        "v55_production_deployment_dry_run",
        "v56_live_paper_trading_staging",
        "v57_live_alpha_signal_integration",
        "v58_broker_integration_planning",
        "v59_manual_approval_gate",
        "v510_broker_sandbox_readiness",
        "v511_sandbox_simulation_harness",
        "v512_sandbox_simulation_robustness",
        "v513_sandbox_connector_contract",
        "v514_sandbox_connector_mock",
        "v515_broker_adapter_skeleton",
        "v516_sandbox_bridge",
        "v517_integration_test_harness",
        "v518_transition_blueprint",
        "v519_provider_selection",
        "v520_provider_onboarding",
        "v521_provider_connector_design",
        "v522_provider_mock_contract",
        "v523_provider_offline_replay",
        "v524_provider_fault_injection",
    ]:
        assert Path(f"tests/test_{version}.py").exists()


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

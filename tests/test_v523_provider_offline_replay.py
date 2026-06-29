from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}
SCENARIOS = {
    "normal_order_lifecycle",
    "partial_fill_lifecycle",
    "rejected_order_lifecycle",
    "canceled_order_lifecycle",
    "timeout_then_recovery",
    "duplicate_order_replay",
    "rate_limit_then_backoff",
    "market_closed_rejection",
    "insufficient_funds_rejection",
    "state_machine_error_recovery",
}
FALSE_KEYS = [
    "replay_runtime_enabled",
    "sandbox_api_enabled",
    "account_read_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_offline_replay_config_defaults_and_blocks_real_path_env(monkeypatch):
    from config.v5_provider_offline_replay_config import (
        get_offline_replay_mode,
        get_offline_replay_provider,
        get_offline_replay_status,
    )

    assert get_offline_replay_mode() == "offline_replay_only"
    assert get_offline_replay_provider() in PROVIDERS
    status = get_offline_replay_status()
    assert status["version"] == "V5.23"
    assert status["offline_replay_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_REPLAY_RUNTIME", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ACCOUNT_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_offline_replay_status()

    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "replay runtime requested but blocked in v5.23" in warnings
    assert "sandbox api requested but blocked in v5.23" in warnings
    assert "account read requested but blocked in v5.23" in warnings
    assert "order submission requested but blocked in v5.23" in warnings
    assert "real money requested but blocked in v5.23" in warnings
    assert _is_safe(blocked)


def test_replay_event_catalog_loader_and_events_are_placeholder_only():
    from provider_offline_replay.replay_event_catalog import build_replay_event_catalog
    from provider_offline_replay.replay_event_loader import (
        load_all_replay_scenarios,
        load_replay_scenario,
    )

    catalog = build_replay_event_catalog("alpaca")
    loaded = load_replay_scenario("alpaca", "normal_order_lifecycle")
    all_loaded = load_all_replay_scenarios("alpaca")

    assert catalog["provider"] == "alpaca"
    assert set(catalog["scenarios"]) >= SCENARIOS
    assert loaded["loaded"] is True
    assert loaded["scenario"] == "normal_order_lifecycle"
    assert all_loaded["loaded"] is True
    assert set(all_loaded["scenarios"]) >= SCENARIOS
    assert "SUBMISSION_BLOCKED" in [event["event_type"] for event in loaded["events"]]
    assert "AUDIT_EVENT_WRITTEN" in [event["event_type"] for event in loaded["events"]]
    assert catalog["offline_replay_only"] is True
    assert _is_safe(catalog)
    assert _is_safe(loaded)


def test_replay_state_machine_blocks_real_submission_states():
    from provider_offline_replay.replay_state_machine import (
        is_terminal_state,
        transition,
        valid_transition_map,
    )

    mapping = valid_transition_map()

    assert "SUBMISSION_BLOCKED" in mapping["APPROVAL_SIMULATED"]
    assert "SUBMITTED" not in json.dumps(mapping)
    assert "SANDBOX_SUBMITTED" not in json.dumps(mapping)
    assert transition("APPROVAL_SIMULATED", "SUBMISSION_BLOCKED")["next_state"] == "SUBMISSION_BLOCKED"
    assert transition("SUBMISSION_BLOCKED", "PROVIDER_ACCEPTED_PLACEHOLDER")["accepted"] is True
    assert is_terminal_state("AUDIT_WRITTEN") is True


def test_replay_runner_runs_lifecycle_failure_and_recovery_scenarios():
    from provider_offline_replay.replay_runner import (
        run_all_replay_scenarios,
        run_replay_scenario,
    )

    normal = run_replay_scenario("alpaca", "normal_order_lifecycle")
    timeout = run_replay_scenario("alpaca", "timeout_then_recovery")
    all_results = run_all_replay_scenarios("alpaca")

    assert normal["scenario"] == "normal_order_lifecycle"
    assert normal["passed"] is True
    assert normal["offline_replay_only"] is True
    assert timeout["passed"] is True
    assert "RECOVERY_REPLAYED" in [step["event_type"] for step in timeout["steps"]]
    assert all_results["total_scenarios"] >= len(SCENARIOS)
    assert all(result["passed"] for result in all_results["results"])
    assert _is_safe(normal)
    assert _is_safe(timeout)


def test_consistency_recovery_audit_safety_and_orchestrator_pass_or_warn():
    from provider_offline_replay.offline_replay_orchestrator import run_offline_replay
    from provider_offline_replay.replay_audit_trail import build_all_replay_audit_trails
    from provider_offline_replay.replay_consistency_validator import (
        validate_all_replay_consistency,
    )
    from provider_offline_replay.replay_failure_recovery_validator import (
        validate_failure_recovery,
    )
    from provider_offline_replay.replay_safety_validator import (
        build_replay_safety_summary,
        validate_replay_safety,
    )

    consistency = validate_all_replay_consistency("alpaca")
    recovery = validate_failure_recovery("alpaca")
    audit = build_all_replay_audit_trails("alpaca")
    safety = build_replay_safety_summary()
    summary = run_offline_replay("alpaca")

    assert consistency["valid"] is True
    assert consistency["validated_scenarios"] >= len(SCENARIOS)
    assert recovery["valid"] is True
    assert set(recovery["recovery_scenarios_checked"]) >= {
        "timeout_then_recovery",
        "rate_limit_then_backoff",
        "duplicate_order_replay",
        "state_machine_error_recovery",
    }
    assert audit["valid"] is True
    assert audit["audit_trails"]
    first_audit = audit["audit_trails"][0]["audit_events"][0]
    assert first_audit["audit_event_id_placeholder"].startswith("AUDIT_EVENT_ID_PLACEHOLDER")
    assert first_audit["raw_payload_stored"] is False
    assert first_audit["provider_payload_redacted"] is True
    assert safety["safe"] is True
    assert validate_replay_safety({"replay_runtime_enabled": True})["safe"] is False
    assert validate_replay_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_replay_safety({"account_read_enabled": True})["safe"] is False
    assert validate_replay_safety({"order_submission_enabled": True})["safe"] is False
    assert validate_replay_safety({"payload": "token=demo"})["safe"] is False
    assert validate_replay_safety({"payload": "raw provider payload"})["safe"] is False
    assert validate_replay_safety({"payload": "https://paper-api.alpaca.markets"})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert summary["failed"] == 0
    assert summary["offline_replay_only"] is True
    for item in [consistency, recovery, audit, safety, summary]:
        assert _is_safe(item)


def test_provider_offline_replay_api_endpoints_return_safe_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/provider-offline-replay/status",
        "/api/v5/provider-offline-replay/catalog",
        "/api/v5/provider-offline-replay/load",
        "/api/v5/provider-offline-replay/run",
        "/api/v5/provider-offline-replay/consistency",
        "/api/v5/provider-offline-replay/recovery",
        "/api/v5/provider-offline-replay/audit",
        "/api/v5/provider-offline-replay/safety",
        "/api/v5/provider-offline-replay/summary",
    ]

    for path in paths:
        response = client.get(path)
        payload = response.json()
        encoded = json.dumps(payload).lower()

        assert response.status_code == 200
        assert payload["success"] is True
        assert "offline_replay_only" in encoded
        assert "paper_trading" in encoded
        for key in FALSE_KEYS:
            assert key in encoded
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from provider_offline_replay.provider_offline_replay_report import (
        generate_provider_offline_replay_report,
    )
    from runtime.security_scan import scan_provider_offline_replay_outputs

    report = generate_provider_offline_replay_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_23_provider_offline_replay_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["offline_replay_only"] is True
    assert report["summary"]["provider"] == "alpaca"
    assert scan_provider_offline_replay_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [
        [],
        ["--provider", "alpaca"],
        ["--provider", "ibkr"],
        ["--scenario", "timeout_then_recovery"],
        ["--check", "safety"],
        ["--check", "consistency"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v523_provider_offline_replay.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["offline_replay_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-provider-offline-replay/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_PROVIDER_OFFLINE_REPLAY.md")
    scanner = _read("runtime/security_scan.py")

    for name in [
        "fetchV5ProviderOfflineReplayStatus",
        "fetchV5ProviderOfflineReplayCatalog",
        "fetchV5ProviderOfflineReplayLoad",
        "fetchV5ProviderOfflineReplayRun",
        "fetchV5ProviderOfflineReplayConsistency",
        "fetchV5ProviderOfflineReplayRecovery",
        "fetchV5ProviderOfflineReplayAudit",
        "fetchV5ProviderOfflineReplaySafety",
        "fetchV5ProviderOfflineReplaySummary",
    ]:
        assert name in api_client
    for label in [
        "Offline Replay Status",
        "Replay Scenario Catalog",
        "Replay Loader",
        "Replay Runner",
        "Consistency Validation",
        "Failure Recovery",
        "Audit Trail",
        "Safety Validation",
        "Final Summary",
    ]:
        assert label in page
    assert "V5 Offline Replay" in shell
    assert "V5.23 Provider Sandbox Connector Offline Replay Harness" in docs
    assert "scan_provider_offline_replay_outputs" in scanner


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

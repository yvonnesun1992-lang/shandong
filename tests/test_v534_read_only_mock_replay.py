from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "mock_replay_runtime_enabled",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "position_read_enabled",
    "balance_read_enabled",
    "order_preview_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_read_only_mock_replay_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_read_only_mock_replay_config import (
        get_read_only_mock_replay_mode,
        get_read_only_mock_replay_provider,
        get_read_only_mock_replay_status,
    )

    assert get_read_only_mock_replay_mode() == "read_only_mock_replay_only"
    assert get_read_only_mock_replay_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_read_only_mock_replay_status()
    assert status["version"] == "V5.34"
    assert status["read_only_mock_replay_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    for env_name in [
        "SHANDONG_V5_ENABLE_READ_ONLY_MOCK_REPLAY_RUNTIME",
        "SHANDONG_V5_ENABLE_SANDBOX_API",
        "SHANDONG_V5_ENABLE_SECRET_READ",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ",
        "SHANDONG_V5_ENABLE_POSITION_READ",
        "SHANDONG_V5_ENABLE_BALANCE_READ",
        "SHANDONG_V5_ENABLE_ORDER_PREVIEW",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION",
        "SHANDONG_V5_ENABLE_REAL_MONEY",
    ]:
        monkeypatch.setenv(env_name, "true")
    blocked = get_read_only_mock_replay_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "mock replay runtime requested but blocked in v5.34" in warnings
    assert "sandbox api requested but blocked in v5.34" in warnings
    assert "secret read requested but blocked in v5.34" in warnings
    assert "account read requested but blocked in v5.34" in warnings
    assert "position read requested but blocked in v5.34" in warnings
    assert "balance read requested but blocked in v5.34" in warnings
    assert "order preview requested but blocked in v5.34" in warnings
    assert "order submission requested but blocked in v5.34" in warnings
    assert "real money requested but blocked in v5.34" in warnings
    assert _is_safe(blocked)


def test_mock_payload_catalog_schema_redaction_replay_audit_safety_and_orchestrator():
    from sandbox_read_only_mock_replay.mock_read_only_payloads import (
        PAYLOAD_TYPES,
        build_all_mock_read_only_payloads,
        build_mock_read_only_payload,
    )
    from sandbox_read_only_mock_replay.read_only_audit_replay import build_read_only_mock_audit_event, build_read_only_mock_audit_trail
    from sandbox_read_only_mock_replay.read_only_mock_replay_orchestrator import run_read_only_mock_replay, summarize_read_only_mock_replay
    from sandbox_read_only_mock_replay.read_only_mock_replay_safety_validator import (
        build_read_only_mock_replay_safety_summary,
        validate_read_only_mock_replay_safety,
    )
    from sandbox_read_only_mock_replay.read_only_replay_runner import run_read_only_replay, run_read_only_replay_payload
    from sandbox_read_only_mock_replay.read_only_schema_validator import (
        validate_account_schema,
        validate_all_read_only_schemas,
        validate_balance_schema,
        validate_position_schema,
    )
    from sandbox_read_only_mock_replay.redaction_replay_validator import (
        validate_all_payload_redaction,
        validate_payload_redaction,
    )

    payloads = build_all_mock_read_only_payloads("alpaca")
    account_payload = build_mock_read_only_payload("alpaca", "account_snapshot_placeholder")
    balance_payload = build_mock_read_only_payload("alpaca", "balance_snapshot_placeholder")
    position_payload = build_mock_read_only_payload("alpaca", "position_snapshot_placeholder")
    schema = validate_all_read_only_schemas("alpaca")
    redaction = validate_all_payload_redaction("alpaca")
    replay = run_read_only_replay("alpaca")
    single = run_read_only_replay_payload("alpaca", "balance_snapshot_placeholder")
    audit_event = build_read_only_mock_audit_event("alpaca", "balance_snapshot_placeholder")
    audit_trail = build_read_only_mock_audit_trail("alpaca")
    safety = build_read_only_mock_replay_safety_summary()
    orchestration = run_read_only_mock_replay("alpaca")
    summary = summarize_read_only_mock_replay(orchestration)

    assert set(PAYLOAD_TYPES).issubset({payload["payload_type"] for payload in payloads["payloads"]})
    assert account_payload["account_ref"] == "ACCOUNT_REF_PLACEHOLDER"
    assert balance_payload["cash_balance"] == "REDACTED_PLACEHOLDER"
    assert balance_payload["buying_power"] == "REDACTED_PLACEHOLDER"
    assert position_payload["market_value"] == "REDACTED_PLACEHOLDER"
    assert position_payload["quantity"] == "REDACTED_PLACEHOLDER"
    for payload in payloads["payloads"]:
        assert payload["raw_payload_stored"] is False
        assert payload["provider_payload_redacted"] is True
        assert payload["values_redacted"] is True
        assert _is_safe(payload)

    assert validate_account_schema(account_payload)["schema_valid"] is True
    assert validate_balance_schema(balance_payload)["schema_valid"] is True
    assert validate_position_schema(position_payload)["schema_valid"] is True
    assert schema["schema_valid"] is True
    assert redaction["redaction_valid"] is True
    assert validate_payload_redaction({"cash_balance": 100})["redaction_valid"] is False
    assert validate_payload_redaction({"quantity": 10})["redaction_valid"] is False
    assert validate_payload_redaction({"market_value": 1234})["redaction_valid"] is False
    assert replay["accepted_count"] > 0
    assert replay["account_read_enabled"] is False
    assert replay["balance_read_enabled"] is False
    assert replay["position_read_enabled"] is False
    assert replay["order_submission_enabled"] is False
    assert single["schema_valid"] is True
    assert single["redaction_valid"] is True
    assert single["audit_written"] is True
    assert audit_event["read_only_mock_audit_id_placeholder"] == "READ_ONLY_MOCK_AUDIT_PLACEHOLDER"
    assert audit_event["account_read"] is False
    assert audit_event["balance_read"] is False
    assert audit_event["position_read"] is False
    assert audit_event["order_submitted"] is False
    assert audit_trail["audit_events"]
    assert safety["safe"] is True
    for key in FALSE_KEYS:
        assert validate_read_only_mock_replay_safety({key: True})["safe"] is False
    assert validate_read_only_mock_replay_safety({"payload": "secret_value=demo"})["safe"] is False
    assert validate_read_only_mock_replay_safety({"cash_balance": 123})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    for item in [payloads, schema, redaction, replay, single, audit_event, audit_trail, safety, summary]:
        assert item["read_only_mock_replay_only"] is True
        assert _is_safe(item)


def test_read_only_mock_replay_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/read-only-mock-replay/status",
        "/api/v5/read-only-mock-replay/payloads",
        "/api/v5/read-only-mock-replay/schema",
        "/api/v5/read-only-mock-replay/redaction",
        "/api/v5/read-only-mock-replay/run",
        "/api/v5/read-only-mock-replay/audit",
        "/api/v5/read-only-mock-replay/safety",
        "/api/v5/read-only-mock-replay/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "read_only_mock_replay_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from runtime.security_scan import scan_read_only_mock_replay_outputs
    from sandbox_read_only_mock_replay.sandbox_read_only_mock_replay_report import generate_sandbox_read_only_mock_replay_report

    report = generate_sandbox_read_only_mock_replay_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_34_sandbox_read_only_mock_replay_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["read_only_mock_replay_only"] is True
    assert scan_read_only_mock_replay_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "schema"], ["--check", "redaction"], ["--check", "safety"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v534_read_only_mock_replay.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["read_only_mock_replay_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-read-only-mock-replay/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_READ_ONLY_MOCK_REPLAY.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5ReadOnlyMockReplayStatus",
        "fetchV5ReadOnlyMockReplayPayloads",
        "fetchV5ReadOnlyMockReplaySchema",
        "fetchV5ReadOnlyMockReplayRedaction",
        "fetchV5ReadOnlyMockReplayRun",
        "fetchV5ReadOnlyMockReplayAudit",
        "fetchV5ReadOnlyMockReplaySafety",
        "fetchV5ReadOnlyMockReplaySummary",
    ]:
        assert name in api_client
    assert "V5 Read-Only Mock Replay" in shell
    assert "Read-Only Mock Replay" in page
    assert "Mock replay only" in page
    assert "V5.34 Sandbox Read-Only Connector Mock Replay" in docs
    assert "scan_read_only_mock_replay_outputs" in scanner


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
        "mock_replay_runtime_enabled\": true",
        "sandbox_api_enabled\": true",
        "secret_read_enabled\": true",
        "account_read_enabled\": true",
        "position_read_enabled\": true",
        "balance_read_enabled\": true",
        "order_preview_enabled\": true",
        "order_submission_enabled\": true",
        "broker_connected\": true",
        "real_money_enabled\": true",
        "paper-api.",
        "api.alpaca.",
    ]
    return not any(term in text for term in blocked)

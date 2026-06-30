from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "fault_injection_runtime_enabled",
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

FAULT_TYPES = [
    "unredacted_account_id",
    "unredacted_cash_balance",
    "unredacted_buying_power",
    "unredacted_position_quantity",
    "unredacted_market_value",
    "unredacted_unrealized_pnl",
    "raw_provider_payload_present",
    "provider_endpoint_url_present",
    "api_key_present",
    "token_present",
    "stale_snapshot",
    "malformed_account_snapshot",
    "malformed_balance_snapshot",
    "malformed_position_snapshot",
    "audit_write_failure",
    "rate_limit_error",
    "unknown_provider_payload",
    "unexpected_order_preview_flag",
    "unexpected_order_submission_flag",
]


def test_read_only_fault_injection_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_read_only_fault_injection_config import (
        get_read_only_fault_injection_mode,
        get_read_only_fault_injection_provider,
        get_read_only_fault_injection_status,
    )

    assert get_read_only_fault_injection_mode() == "read_only_fault_injection_only"
    assert get_read_only_fault_injection_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_read_only_fault_injection_status()
    assert status["version"] == "V5.35"
    assert status["read_only_fault_injection_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    for env_name in [
        "SHANDONG_V5_ENABLE_READ_ONLY_FAULT_INJECTION_RUNTIME",
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
    blocked = get_read_only_fault_injection_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "fault injection runtime requested but blocked in v5.35" in warnings
    assert "sandbox api requested but blocked in v5.35" in warnings
    assert "secret read requested but blocked in v5.35" in warnings
    assert "account read requested but blocked in v5.35" in warnings
    assert "position read requested but blocked in v5.35" in warnings
    assert "balance read requested but blocked in v5.35" in warnings
    assert "order preview requested but blocked in v5.35" in warnings
    assert "order submission requested but blocked in v5.35" in warnings
    assert "real money requested but blocked in v5.35" in warnings
    assert _is_safe(blocked)


def test_fault_payload_catalog_and_detectors_block_expected_faults():
    from sandbox_read_only_fault_injection.audit_failure_simulator import (
        simulate_audit_write_failure,
        validate_audit_failure_handling,
    )
    from sandbox_read_only_fault_injection.fault_injection_orchestrator import (
        run_read_only_fault_injection,
        summarize_fault_injection,
    )
    from sandbox_read_only_fault_injection.fault_injection_runner import run_fault_case, run_fault_injection
    from sandbox_read_only_fault_injection.fault_injection_safety_validator import (
        build_fault_injection_safety_summary,
        validate_fault_injection_safety,
    )
    from sandbox_read_only_fault_injection.fault_payload_catalog import (
        FAULT_TYPES as CATALOG_TYPES,
        build_all_fault_payloads,
        build_fault_payload,
    )
    from sandbox_read_only_fault_injection.fault_schema_validator import (
        validate_all_fault_schemas,
        validate_fault_schema,
    )
    from sandbox_read_only_fault_injection.order_path_intrusion_detector import (
        detect_all_order_path_intrusions,
        detect_order_path_intrusion,
    )
    from sandbox_read_only_fault_injection.rate_limit_fault_simulator import (
        simulate_rate_limit_fault,
        validate_rate_limit_fault_handling,
    )
    from sandbox_read_only_fault_injection.redaction_failure_detector import (
        detect_all_redaction_failures,
        detect_redaction_failure,
    )
    from sandbox_read_only_fault_injection.stale_snapshot_detector import (
        detect_all_stale_snapshots,
        detect_stale_snapshot,
    )

    catalog = build_all_fault_payloads("alpaca")
    assert set(FAULT_TYPES) == set(CATALOG_TYPES)
    assert {payload["fault_type"] for payload in catalog["fault_payloads"]} == set(FAULT_TYPES)
    assert catalog["read_only_fault_injection_only"] is True

    assert detect_redaction_failure(build_fault_payload("alpaca", "unredacted_account_id"))["redaction_failure_detected"] is True
    assert detect_redaction_failure(build_fault_payload("alpaca", "unredacted_cash_balance"))["redaction_failure_detected"] is True
    assert detect_redaction_failure(build_fault_payload("alpaca", "unredacted_position_quantity"))["redaction_failure_detected"] is True
    assert detect_redaction_failure(build_fault_payload("alpaca", "raw_provider_payload_present"))["redaction_failure_detected"] is True
    assert detect_redaction_failure(build_fault_payload("alpaca", "provider_endpoint_url_present"))["redaction_failure_detected"] is True
    assert detect_all_redaction_failures("alpaca")["redaction_failures_detected"] is True

    assert validate_fault_schema(build_fault_payload("alpaca", "malformed_account_snapshot"))["schema_faults_detected"] is True
    assert validate_fault_schema(build_fault_payload("alpaca", "malformed_balance_snapshot"))["schema_faults_detected"] is True
    assert validate_fault_schema(build_fault_payload("alpaca", "malformed_position_snapshot"))["schema_faults_detected"] is True
    assert validate_all_fault_schemas("alpaca")["schema_faults_detected"] is True

    assert detect_stale_snapshot(build_fault_payload("alpaca", "stale_snapshot"))["stale_detected"] is True
    assert detect_all_stale_snapshots("alpaca")["stale_detected"] is True

    audit_fault = simulate_audit_write_failure("alpaca")
    assert audit_fault["audit_write_success"] is False
    assert audit_fault["audit_fallback_written"] is True
    assert audit_fault["raw_payload_logged"] is False
    assert validate_audit_failure_handling(audit_fault)["audit_failure_detected"] is True

    rate_limit_fault = simulate_rate_limit_fault("alpaca")
    assert rate_limit_fault["rate_limit_error"] is True
    assert rate_limit_fault["retry_allowed"] is False
    assert rate_limit_fault["network_retry_executed"] is False
    assert validate_rate_limit_fault_handling(rate_limit_fault)["rate_limit_fault_detected"] is True

    assert detect_order_path_intrusion(build_fault_payload("alpaca", "unexpected_order_preview_flag"))["order_intrusion_detected"] is True
    assert detect_order_path_intrusion(build_fault_payload("alpaca", "unexpected_order_submission_flag"))["order_intrusion_detected"] is True
    assert detect_all_order_path_intrusions("alpaca")["order_intrusion_detected"] is True

    runner = run_fault_injection("alpaca")
    assert runner["total_fault_cases"] == len(FAULT_TYPES)
    assert runner["blocked_fault_cases"] == len(FAULT_TYPES)
    assert runner["unexpectedly_accepted"] == []
    for result in runner["results"]:
        assert result["accepted"] is False
        assert result["blocked"] is True

    case = run_fault_case("alpaca", "rate_limit_error")
    assert case["accepted"] is False
    assert case["blocked"] is True
    assert case["rate_limit_fault_detected"] is True

    safety = build_fault_injection_safety_summary()
    assert safety["safe"] is True
    for key in FALSE_KEYS:
        assert validate_fault_injection_safety({key: True})["safe"] is False
    assert validate_fault_injection_safety({"payload": "MOCK_API_KEY_FOR_TEST_ONLY"})["safe"] is False
    assert validate_fault_injection_safety({"cash_balance": 123})["safe"] is False

    orchestration = run_read_only_fault_injection("alpaca")
    summary = summarize_fault_injection(orchestration)
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert summary["total_fault_cases"] == len(FAULT_TYPES)
    assert summary["blocked_fault_cases"] == len(FAULT_TYPES)
    assert summary["unexpectedly_accepted"] == []
    for item in [catalog, runner, case, audit_fault, rate_limit_fault, safety, summary]:
        assert item["read_only_fault_injection_only"] is True


def test_read_only_fault_injection_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/read-only-fault-injection/status",
        "/api/v5/read-only-fault-injection/payloads",
        "/api/v5/read-only-fault-injection/schema",
        "/api/v5/read-only-fault-injection/redaction",
        "/api/v5/read-only-fault-injection/stale",
        "/api/v5/read-only-fault-injection/audit-failure",
        "/api/v5/read-only-fault-injection/rate-limit",
        "/api/v5/read-only-fault-injection/order-intrusion",
        "/api/v5/read-only-fault-injection/run",
        "/api/v5/read-only-fault-injection/safety",
        "/api/v5/read-only-fault-injection/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "read_only_fault_injection_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from runtime.security_scan import scan_read_only_fault_injection_outputs
    from sandbox_read_only_fault_injection.sandbox_read_only_fault_injection_report import (
        generate_sandbox_read_only_fault_injection_report,
    )

    report = generate_sandbox_read_only_fault_injection_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_35_sandbox_read_only_fault_injection_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["read_only_fault_injection_only"] is True
    assert scan_read_only_fault_injection_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [
        [],
        ["--provider", "alpaca"],
        ["--provider", "ibkr"],
        ["--check", "redaction"],
        ["--check", "stale"],
        ["--check", "order-intrusion"],
        ["--check", "safety"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v535_read_only_fault_injection.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["read_only_fault_injection_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-read-only-fault-injection/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_READ_ONLY_FAULT_INJECTION.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5ReadOnlyFaultInjectionStatus",
        "fetchV5ReadOnlyFaultInjectionPayloads",
        "fetchV5ReadOnlyFaultInjectionSchema",
        "fetchV5ReadOnlyFaultInjectionRedaction",
        "fetchV5ReadOnlyFaultInjectionStale",
        "fetchV5ReadOnlyFaultInjectionAuditFailure",
        "fetchV5ReadOnlyFaultInjectionRateLimit",
        "fetchV5ReadOnlyFaultInjectionOrderIntrusion",
        "fetchV5ReadOnlyFaultInjectionRun",
        "fetchV5ReadOnlyFaultInjectionSafety",
        "fetchV5ReadOnlyFaultInjectionSummary",
    ]:
        assert name in api_client
    assert "V5 Read-Only Fault Injection" in shell
    assert "Read-Only Fault Injection" in page
    assert "Fault injection only" in page
    assert "V5.35 Sandbox Read-Only Connector Fault Injection" in docs
    assert "scan_read_only_fault_injection_outputs" in scanner


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _is_safe(payload: object) -> bool:
    text = json.dumps(payload, default=str).lower()
    blocked = [
        "api_key=demo",
        "secret_value=demo",
        "token=demo",
        "password=demo",
        "authorization: bearer",
        "real_order_id_",
        "real_account_id",
        "paper-api.",
        "api.alpaca.",
        "fault_injection_runtime_enabled\": true",
        "sandbox_api_enabled\": true",
        "secret_read_enabled\": true",
        "account_read_enabled\": true",
        "position_read_enabled\": true",
        "balance_read_enabled\": true",
        "order_preview_enabled\": true",
        "order_submission_enabled\": true",
        "broker_connected\": true",
        "real_money_enabled\": true",
    ]
    return not any(term in text for term in blocked)

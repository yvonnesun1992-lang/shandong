from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "stability_gate_runtime_enabled",
    "stability_gate_passed",
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


def test_read_only_stability_gate_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_read_only_stability_gate_config import (
        get_read_only_stability_gate_mode,
        get_read_only_stability_gate_provider,
        get_read_only_stability_gate_status,
    )

    assert get_read_only_stability_gate_mode() == "read_only_stability_gate_only"
    assert get_read_only_stability_gate_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_read_only_stability_gate_status()
    assert status["version"] == "V5.36"
    assert status["read_only_stability_gate_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    for env_name in [
        "SHANDONG_V5_ENABLE_READ_ONLY_STABILITY_GATE_RUNTIME",
        "SHANDONG_V5_ENABLE_STABILITY_GATE_PASS",
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
    blocked = get_read_only_stability_gate_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "stability gate runtime requested but blocked in v5.36" in warnings
    assert "stability gate pass requested but blocked in v5.36" in warnings
    assert "sandbox api requested but blocked in v5.36" in warnings
    assert "secret read requested but blocked in v5.36" in warnings
    assert "account read requested but blocked in v5.36" in warnings
    assert "position read requested but blocked in v5.36" in warnings
    assert "balance read requested but blocked in v5.36" in warnings
    assert "order preview requested but blocked in v5.36" in warnings
    assert "order submission requested but blocked in v5.36" in warnings
    assert "real money requested but blocked in v5.36" in warnings
    assert _is_safe(blocked)


def test_stability_gate_collectors_checks_decision_and_safety():
    from sandbox_read_only_stability_gate.audit_stability_check import check_audit_stability
    from sandbox_read_only_stability_gate.fault_evidence_collector import collect_fault_evidence, summarize_fault_evidence
    from sandbox_read_only_stability_gate.order_path_stability_check import check_order_path_stability
    from sandbox_read_only_stability_gate.redaction_stability_check import check_redaction_stability
    from sandbox_read_only_stability_gate.replay_evidence_collector import collect_replay_evidence, summarize_replay_evidence
    from sandbox_read_only_stability_gate.schema_stability_check import check_schema_stability
    from sandbox_read_only_stability_gate.stability_gate_decision import (
        build_stability_gate_decision,
        evaluate_stability_gate_decision,
    )
    from sandbox_read_only_stability_gate.stability_gate_orchestrator import (
        run_read_only_stability_gate,
        summarize_stability_gate,
    )
    from sandbox_read_only_stability_gate.stability_gate_safety_validator import (
        build_stability_gate_safety_summary,
        validate_stability_gate_safety,
    )

    replay = collect_replay_evidence("alpaca")
    replay_summary = summarize_replay_evidence(replay)
    fault = collect_fault_evidence("alpaca")
    fault_summary = summarize_fault_evidence(fault)
    redaction = check_redaction_stability("alpaca")
    schema = check_schema_stability("alpaca")
    audit = check_audit_stability("alpaca")
    order = check_order_path_stability("alpaca")
    decision = build_stability_gate_decision("alpaca")
    evaluated = evaluate_stability_gate_decision({"replay_passed": True, "fault_injection_passed": True, "simulated_approval": True})
    safety = build_stability_gate_safety_summary()
    orchestration = run_read_only_stability_gate("alpaca")
    summary = summarize_stability_gate(orchestration)

    assert replay["replay_evidence_ready"] is True
    assert replay["mock_replay_passed"] is True
    assert replay_summary["mock_replay_passed"] is True
    assert fault["fault_evidence_ready"] is True
    assert fault["fault_injection_passed"] is True
    assert fault_summary["fault_injection_passed"] is True
    assert redaction["redaction_stable"] is True
    assert schema["schema_stable"] is True
    assert audit["audit_stable"] is True
    assert order["order_path_stable"] is True
    assert order["order_path_blocked"] is True
    for item in [decision, evaluated, summary]:
        assert item["decision"] == "STABILITY_GATE_BLOCKED"
        assert item["stability_gate_passed"] is False
        assert item["read_only_connector_allowed"] is False
    assert safety["safe"] is True
    for key in FALSE_KEYS:
        assert validate_stability_gate_safety({key: True})["safe"] is False
    assert validate_stability_gate_safety({"payload": "MOCK_API_KEY_FOR_TEST_ONLY"})["safe"] is False
    assert validate_stability_gate_safety({"cash_balance": 123})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    for item in [replay, replay_summary, fault, fault_summary, redaction, schema, audit, order, decision, evaluated, safety, summary]:
        assert item["read_only_stability_gate_only"] is True
        assert _is_safe(item)


def test_read_only_stability_gate_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/read-only-stability-gate/status",
        "/api/v5/read-only-stability-gate/replay-evidence",
        "/api/v5/read-only-stability-gate/fault-evidence",
        "/api/v5/read-only-stability-gate/redaction",
        "/api/v5/read-only-stability-gate/schema",
        "/api/v5/read-only-stability-gate/audit",
        "/api/v5/read-only-stability-gate/order-path",
        "/api/v5/read-only-stability-gate/decision",
        "/api/v5/read-only-stability-gate/safety",
        "/api/v5/read-only-stability-gate/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "read_only_stability_gate_only" in text
        assert "paper_trading" in text
        assert "stability_gate_passed" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from runtime.security_scan import scan_read_only_stability_gate_outputs
    from sandbox_read_only_stability_gate.sandbox_read_only_stability_gate_report import (
        generate_sandbox_read_only_stability_gate_report,
    )

    report = generate_sandbox_read_only_stability_gate_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_36_sandbox_read_only_stability_gate_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["read_only_stability_gate_only"] is True
    assert scan_read_only_stability_gate_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [
        [],
        ["--provider", "alpaca"],
        ["--provider", "ibkr"],
        ["--check", "replay"],
        ["--check", "fault"],
        ["--check", "redaction"],
        ["--check", "schema"],
        ["--check", "order-path"],
        ["--check", "decision"],
        ["--check", "safety"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v536_read_only_stability_gate.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["read_only_stability_gate_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-read-only-stability-gate/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_READ_ONLY_STABILITY_GATE.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5ReadOnlyStabilityGateStatus",
        "fetchV5ReadOnlyStabilityGateReplayEvidence",
        "fetchV5ReadOnlyStabilityGateFaultEvidence",
        "fetchV5ReadOnlyStabilityGateRedaction",
        "fetchV5ReadOnlyStabilityGateSchema",
        "fetchV5ReadOnlyStabilityGateAudit",
        "fetchV5ReadOnlyStabilityGateOrderPath",
        "fetchV5ReadOnlyStabilityGateDecision",
        "fetchV5ReadOnlyStabilityGateSafety",
        "fetchV5ReadOnlyStabilityGateSummary",
    ]:
        assert name in api_client
    assert "V5 Read-Only Stability Gate" in shell
    assert "Read-Only Stability Gate" in page
    assert "Stability gate only" in page
    assert "V5.36 Sandbox Read-Only Connector Stability Gate" in docs
    assert "scan_read_only_stability_gate_outputs" in scanner


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
        "stability_gate_runtime_enabled\": true",
        "stability_gate_passed\": true",
        "sandbox_api_enabled\": true",
        "secret_read_enabled\": true",
        "account_read_enabled\": true",
        "position_read_enabled\": true",
        "balance_read_enabled\": true",
        "order_preview_enabled\": true",
        "order_submission_enabled\": true",
        "broker_connected\": true",
        "real_money_enabled\": true",
        "read_only_connector_allowed\": true",
    ]
    return not any(term in text for term in blocked)

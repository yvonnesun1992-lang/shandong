from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "approval_runtime_enabled",
    "operator_approval_granted",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "broker_connected",
    "order_submission_enabled",
    "real_money_enabled",
]


def test_pre_sandbox_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_pre_sandbox_approval_config import (
        get_pre_sandbox_approval_mode,
        get_pre_sandbox_approval_provider,
        get_pre_sandbox_approval_status,
    )

    assert get_pre_sandbox_approval_mode() == "approval_gate_only"
    assert get_pre_sandbox_approval_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_pre_sandbox_approval_status()
    assert status["version"] == "V5.28"
    assert status["approval_gate_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_OPERATOR_APPROVAL_GRANTED", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_APPROVAL_RUNTIME", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SECRET_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_pre_sandbox_approval_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "simulated operator approval requested but blocked in v5.28" in warnings
    assert "approval runtime requested but blocked in v5.28" in warnings
    assert "sandbox api requested but blocked in v5.28" in warnings
    assert "secret read requested but blocked in v5.28" in warnings
    assert "order submission requested but blocked in v5.28" in warnings
    assert "real money requested but blocked in v5.28" in warnings
    assert _is_safe(blocked)


def test_approval_schema_policies_gate_audit_safety_and_orchestrator():
    from pre_sandbox_approval.approval_audit_trail import build_approval_audit_event, build_approval_audit_trail
    from pre_sandbox_approval.approval_gate_evaluator import build_approval_gate_summary, evaluate_pre_sandbox_approval_gate
    from pre_sandbox_approval.approval_request_schema import build_approval_request_schema
    from pre_sandbox_approval.approval_safety_validator import build_approval_safety_summary, validate_approval_safety
    from pre_sandbox_approval.evidence_requirement_validator import validate_evidence_requirements
    from pre_sandbox_approval.operator_role_policy import build_operator_role_policy
    from pre_sandbox_approval.pre_sandbox_approval_orchestrator import run_pre_sandbox_approval_review, summarize_approval_review
    from pre_sandbox_approval.risk_acknowledgement_policy import build_risk_acknowledgement_policy

    schema = build_approval_request_schema("alpaca")
    evidence = validate_evidence_requirements("alpaca")
    roles = build_operator_role_policy()
    risk = build_risk_acknowledgement_policy()
    gate = evaluate_pre_sandbox_approval_gate({"provider": "alpaca", "simulated_operator_approval": True})
    gate_summary = build_approval_gate_summary("alpaca")
    audit_event = build_approval_audit_event({"provider": "alpaca", "requested_action": "sandbox_dry_run"})
    audit_trail = build_approval_audit_trail("alpaca")
    safety = build_approval_safety_summary()
    review = run_pre_sandbox_approval_review("alpaca")
    summary = summarize_approval_review(review)

    assert schema["approval_request_id_placeholder"] == "APPROVAL_REQUEST_PLACEHOLDER"
    assert schema["risk_acknowledgement_required"] is True
    assert evidence["approval_gate_only"] is True
    assert evidence["evidence_ready"] is False
    assert "sandbox entry gate currently blocked" in " ".join(evidence["blocking_items"]).lower()
    assert roles["roles"]["technical_operator"]["approval_enabled"] is False
    assert roles["rules"]["single_operator_can_approve_order_submission"] is False
    assert risk["acknowledgements"]["no_real_money"] is True
    assert risk["acknowledgements"]["manual_approval_remains_required"] is True
    assert gate["approval_gate"] == "BLOCKED"
    assert gate["operator_approval_granted"] is False
    assert gate_summary["approval_gate"] == "BLOCKED"
    assert "simulated approval requested but blocked in v5.28" in " ".join(gate["warnings"]).lower()
    assert audit_event["approval_audit_id_placeholder"] == "APPROVAL_AUDIT_PLACEHOLDER"
    assert audit_event["raw_secret_logged"] is False
    assert audit_event["provider_payload_redacted"] is True
    assert audit_trail["audit_enabled"] is False
    assert safety["safe"] is True
    assert validate_approval_safety({"approval_runtime_enabled": True})["safe"] is False
    assert validate_approval_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_approval_safety({"secret_read_enabled": True})["safe"] is False
    assert validate_approval_safety({"order_submission_enabled": True})["safe"] is False
    assert validate_approval_safety({"payload": "api_key=demo"})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    for item in [schema, evidence, roles, risk, gate, gate_summary, audit_event, audit_trail, safety, summary]:
        assert item["approval_gate_only"] is True
        assert _is_safe(item)


def test_pre_sandbox_approval_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/pre-sandbox-approval/status",
        "/api/v5/pre-sandbox-approval/request-schema",
        "/api/v5/pre-sandbox-approval/evidence",
        "/api/v5/pre-sandbox-approval/roles",
        "/api/v5/pre-sandbox-approval/risk-acknowledgement",
        "/api/v5/pre-sandbox-approval/gate",
        "/api/v5/pre-sandbox-approval/audit",
        "/api/v5/pre-sandbox-approval/safety",
        "/api/v5/pre-sandbox-approval/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "approval_gate_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from pre_sandbox_approval.pre_sandbox_approval_report import generate_pre_sandbox_approval_report
    from runtime.security_scan import scan_pre_sandbox_approval_outputs

    report = generate_pre_sandbox_approval_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_28_pre_sandbox_approval_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["approval_gate_only"] is True
    assert scan_pre_sandbox_approval_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "evidence"], ["--check", "gate"], ["--check", "safety"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v528_pre_sandbox_approval.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["approval_gate_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-pre-sandbox-approval/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_PRE_SANDBOX_APPROVAL.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5PreSandboxApprovalStatus",
        "fetchV5PreSandboxApprovalRequestSchema",
        "fetchV5PreSandboxApprovalEvidence",
        "fetchV5PreSandboxApprovalRoles",
        "fetchV5PreSandboxApprovalRiskAcknowledgement",
        "fetchV5PreSandboxApprovalGate",
        "fetchV5PreSandboxApprovalAudit",
        "fetchV5PreSandboxApprovalSafety",
        "fetchV5PreSandboxApprovalSummary",
    ]:
        assert name in api_client
    assert "V5 Pre-Sandbox Approval" in shell
    assert "Pre-Sandbox Approval Status" in page
    assert "Operator Approval Gate" in page
    assert "V5.28 Pre-Sandbox Operator Approval Gate" in docs
    assert "scan_pre_sandbox_approval_outputs" in scanner


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
        "sandbox_api_enabled\": true",
        "secret_read_enabled\": true",
        "operator_approval_granted\": true",
        "order_submission_enabled\": true",
        "broker_connected\": true",
        "real_money_enabled\": true",
        "paper-api.",
        "api.alpaca.",
    ]
    return not any(term in text for term in blocked)

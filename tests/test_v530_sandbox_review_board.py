from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "review_runtime_enabled",
    "reviewer_approval_enabled",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_review_board_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_sandbox_review_board_config import (
        get_review_board_mode,
        get_review_board_provider,
        get_review_board_status,
    )

    assert get_review_board_mode() == "review_board_only"
    assert get_review_board_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_review_board_status()
    assert status["version"] == "V5.30"
    assert status["review_board_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_REVIEW_RUNTIME", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REVIEWER_APPROVAL", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SECRET_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ACCOUNT_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_review_board_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "review runtime requested but blocked in v5.30" in warnings
    assert "reviewer approval requested but blocked in v5.30" in warnings
    assert "sandbox api requested but blocked in v5.30" in warnings
    assert "secret read requested but blocked in v5.30" in warnings
    assert "account read requested but blocked in v5.30" in warnings
    assert "order submission requested but blocked in v5.30" in warnings
    assert "real money requested but blocked in v5.30" in warnings
    assert _is_safe(blocked)


def test_review_board_components_decision_safety_and_orchestrator():
    from sandbox_review_board.evidence_review_matrix import build_evidence_review_matrix
    from sandbox_review_board.go_no_go_decision_record import build_go_no_go_decision, evaluate_review_board_decision
    from sandbox_review_board.readiness_scoring import build_readiness_score_summary, compute_readiness_score
    from sandbox_review_board.review_audit_trail import build_review_audit_event, build_review_audit_trail
    from sandbox_review_board.review_board_charter import build_review_board_charter
    from sandbox_review_board.review_board_orchestrator import build_review_board_packet, summarize_review_board_packet
    from sandbox_review_board.review_board_safety_validator import build_review_board_safety_summary, validate_review_board_safety
    from sandbox_review_board.reviewer_role_matrix import build_reviewer_role_matrix
    from sandbox_review_board.risk_acceptance_matrix import build_risk_acceptance_matrix

    charter = build_review_board_charter("alpaca")
    roles = build_reviewer_role_matrix("alpaca")
    evidence = build_evidence_review_matrix("alpaca")
    risks = build_risk_acceptance_matrix("alpaca")
    score = compute_readiness_score("alpaca")
    score_summary = build_readiness_score_summary("alpaca")
    decision = build_go_no_go_decision("alpaca")
    simulated = evaluate_review_board_decision({"provider": "alpaca", "simulated_approval": True})
    audit_event = build_review_audit_event("alpaca", "review_decision")
    audit_trail = build_review_audit_trail("alpaca")
    safety = build_review_board_safety_summary()
    packet = build_review_board_packet("alpaca")
    summary = summarize_review_board_packet(packet)

    assert charter["charter"]["decision_authority"] == ["NO_GO", "REVIEW_REQUIRED", "BLOCKED"]
    assert charter["charter"]["no_execution_policy"] is True
    for role in roles["roles"].values():
        assert role["can_approve_sandbox_api"] is False
        assert role["can_approve_secret_read"] is False
        assert role["can_approve_account_read"] is False
        assert role["can_approve_order_submission"] is False
        assert role["can_override_no_go"] is False
    assert evidence["evidence_ready"] is False
    assert "missing production requirements" in " ".join(evidence["blocking_items"]).lower()
    assert risks["risk_acceptance_ready"] is False
    assert risks["accepted_risks"] == []
    assert risks["blocked_risks"]
    assert score["ready_for_sandbox_dry_run"] is False
    assert score_summary["ready_for_sandbox_dry_run"] is False
    assert decision["decision"] == "NO_GO"
    assert decision["sandbox_dry_run_allowed"] is False
    assert simulated["decision"] == "NO_GO"
    assert simulated["sandbox_dry_run_allowed"] is False
    assert audit_event["review_audit_id_placeholder"] == "REVIEW_AUDIT_PLACEHOLDER"
    assert audit_event["raw_secret_logged"] is False
    assert audit_event["account_read"] is False
    assert audit_event["order_submitted"] is False
    assert audit_trail["external_log_upload"] is False
    assert safety["safe"] is True
    assert validate_review_board_safety({"review_runtime_enabled": True})["safe"] is False
    assert validate_review_board_safety({"reviewer_approval_enabled": True})["safe"] is False
    assert validate_review_board_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_review_board_safety({"secret_read_enabled": True})["safe"] is False
    assert validate_review_board_safety({"account_read_enabled": True})["safe"] is False
    assert validate_review_board_safety({"order_submission_enabled": True})["safe"] is False
    assert validate_review_board_safety({"payload": "api_key=demo"})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    for item in [charter, roles, evidence, risks, score, score_summary, decision, simulated, audit_event, audit_trail, safety, summary]:
        assert item["review_board_only"] is True
        assert _is_safe(item)


def test_sandbox_review_board_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/sandbox-review-board/status",
        "/api/v5/sandbox-review-board/charter",
        "/api/v5/sandbox-review-board/roles",
        "/api/v5/sandbox-review-board/evidence",
        "/api/v5/sandbox-review-board/risks",
        "/api/v5/sandbox-review-board/score",
        "/api/v5/sandbox-review-board/decision",
        "/api/v5/sandbox-review-board/audit",
        "/api/v5/sandbox-review-board/safety",
        "/api/v5/sandbox-review-board/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "review_board_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from runtime.security_scan import scan_sandbox_review_board_outputs
    from sandbox_review_board.sandbox_review_board_report import generate_sandbox_review_board_report

    report = generate_sandbox_review_board_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_30_sandbox_review_board_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["review_board_only"] is True
    assert scan_sandbox_review_board_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "evidence"], ["--check", "risks"], ["--check", "decision"], ["--check", "safety"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v530_sandbox_review_board.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["review_board_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-sandbox-review-board/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_SANDBOX_REVIEW_BOARD.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5SandboxReviewBoardStatus",
        "fetchV5SandboxReviewBoardCharter",
        "fetchV5SandboxReviewBoardRoles",
        "fetchV5SandboxReviewBoardEvidence",
        "fetchV5SandboxReviewBoardRisks",
        "fetchV5SandboxReviewBoardScore",
        "fetchV5SandboxReviewBoardDecision",
        "fetchV5SandboxReviewBoardAudit",
        "fetchV5SandboxReviewBoardSafety",
        "fetchV5SandboxReviewBoardSummary",
    ]:
        assert name in api_client
    assert "V5 Review Board" in shell
    assert "Sandbox Review Board" in page
    assert "Go / No-Go Decision" in page
    assert "V5.30 Sandbox Dry-Run Readiness Review Board" in docs
    assert "scan_sandbox_review_board_outputs" in scanner


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

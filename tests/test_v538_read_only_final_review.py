from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "final_review_runtime_enabled",
    "final_review_passed",
    "read_only_connector_allowed",
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


def test_read_only_final_review_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_read_only_final_review_config import (
        get_read_only_final_review_mode,
        get_read_only_final_review_provider,
        get_read_only_final_review_status,
    )

    assert get_read_only_final_review_mode() == "read_only_final_review_only"
    assert get_read_only_final_review_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_read_only_final_review_status()
    assert status["version"] == "V5.38"
    assert status["read_only_final_review_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_READ_ONLY_FINAL_REVIEW_MODE", "production")
    for env_name in [
        "SHANDONG_V5_ENABLE_READ_ONLY_FINAL_REVIEW_RUNTIME",
        "SHANDONG_V5_ENABLE_FINAL_REVIEW_PASS",
        "SHANDONG_V5_ENABLE_READ_ONLY_CONNECTOR",
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
    blocked = get_read_only_final_review_status()
    warnings = " | ".join(blocked["warnings"]).lower()
    assert get_read_only_final_review_mode() == "read_only_final_review_only"
    assert blocked["read_only_final_review_mode"] == "read_only_final_review_only"
    for key in FALSE_KEYS:
        assert blocked[key] is False
    assert "read-only final review mode override requested but blocked in v5.38" in warnings
    assert "final review runtime requested but blocked in v5.38" in warnings
    assert "final review pass requested but blocked in v5.38" in warnings
    assert "read-only connector requested but blocked in v5.38" in warnings
    assert "sandbox api requested but blocked in v5.38" in warnings
    assert "secret read requested but blocked in v5.38" in warnings
    assert "account read requested but blocked in v5.38" in warnings
    assert "position read requested but blocked in v5.38" in warnings
    assert "balance read requested but blocked in v5.38" in warnings
    assert "order preview requested but blocked in v5.38" in warnings
    assert "order submission requested but blocked in v5.38" in warnings
    assert "real money requested but blocked in v5.38" in warnings
    assert _is_safe(blocked)


def test_final_review_modules_decision_audit_orchestration_and_safety():
    from sandbox_read_only_final_review.evidence_review_matrix import build_evidence_review_matrix
    from sandbox_read_only_final_review.final_review_audit_trail import (
        build_final_review_audit_event,
        build_final_review_audit_trail,
    )
    from sandbox_read_only_final_review.final_review_charter import build_final_review_charter
    from sandbox_read_only_final_review.final_review_decision import (
        build_final_review_decision,
        evaluate_final_review_decision,
    )
    from sandbox_read_only_final_review.final_review_orchestrator import (
        build_read_only_final_review,
        summarize_read_only_final_review,
    )
    from sandbox_read_only_final_review.final_review_safety_validator import (
        build_final_review_safety_summary,
        validate_final_review_safety,
    )
    from sandbox_read_only_final_review.missing_requirement_register import build_missing_requirement_register
    from sandbox_read_only_final_review.reviewer_role_matrix import build_reviewer_role_matrix
    from sandbox_read_only_final_review.risk_acceptance_matrix import build_risk_acceptance_matrix

    provider = "alpaca"
    charter = build_final_review_charter(provider)
    roles = build_reviewer_role_matrix(provider)
    evidence = build_evidence_review_matrix(provider)
    risks = build_risk_acceptance_matrix(provider)
    missing = build_missing_requirement_register(provider)
    decision = build_final_review_decision(provider)
    evaluated = evaluate_final_review_decision(
        {"evidence_review_ready": True, "risk_acceptance_ready": True, "simulated_approval": True}
    )
    audit_event = build_final_review_audit_event(provider, "review_attempt")
    audit = build_final_review_audit_trail(provider)
    safety = build_final_review_safety_summary()
    review = build_read_only_final_review(provider)
    summary = summarize_read_only_final_review(review)

    assert charter["charter"]["decision_authority"] == "review-only"
    for role in roles["roles"]:
        assert role["can_approve_sandbox_api"] is False
        assert role["can_approve_secret_read"] is False
        assert role["can_approve_account_read"] is False
        assert role["can_approve_balance_read"] is False
        assert role["can_approve_position_read"] is False
        assert role["can_approve_order_preview"] is False
        assert role["can_approve_order_submission"] is False
        assert role["can_override_blocked_decision"] is False
    assert evidence["evidence_review_ready"] is True
    assert risks["risk_acceptance_ready"] is False
    assert risks["accepted_risks"] == []
    assert missing["missing_count"] >= 10
    for item in [decision, evaluated, summary]:
        assert item["decision"] == "READ_ONLY_FINAL_REVIEW_ONLY"
        assert item["final_review_passed"] is False
        assert item["read_only_connector_allowed"] is False
    assert audit_event["raw_secret_logged"] is False
    assert audit_event["account_read"] is False
    assert audit_event["balance_read"] is False
    assert audit_event["position_read"] is False
    assert audit_event["order_submitted"] is False
    assert audit["events"]
    assert safety["safe"] is True
    for key in FALSE_KEYS:
        assert validate_final_review_safety({key: True})["safe"] is False
    assert validate_final_review_safety({"payload": "MOCK_API_KEY_FOR_TEST_ONLY"})["safe"] is False
    assert validate_final_review_safety({"cash_balance": 123})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    for item in [charter, roles, evidence, risks, missing, decision, evaluated, audit_event, audit, safety, review, summary]:
        assert item["read_only_final_review_only"] is True
        assert _is_safe(item)


def test_read_only_final_review_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/read-only-final-review/status",
        "/api/v5/read-only-final-review/charter",
        "/api/v5/read-only-final-review/roles",
        "/api/v5/read-only-final-review/evidence",
        "/api/v5/read-only-final-review/risks",
        "/api/v5/read-only-final-review/missing-requirements",
        "/api/v5/read-only-final-review/decision",
        "/api/v5/read-only-final-review/audit",
        "/api/v5/read-only-final-review/safety",
        "/api/v5/read-only-final-review/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "read_only_final_review_only" in text
        assert "paper_trading" in text
        assert "final_review_passed" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from runtime.security_scan import scan_read_only_final_review_outputs
    from sandbox_read_only_final_review.sandbox_read_only_final_review_report import (
        generate_sandbox_read_only_final_review_report,
    )

    report = generate_sandbox_read_only_final_review_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_38_sandbox_read_only_final_review_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["read_only_final_review_only"] is True
    assert scan_read_only_final_review_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [
        [],
        ["--provider", "alpaca"],
        ["--provider", "ibkr"],
        ["--check", "evidence"],
        ["--check", "risks"],
        ["--check", "missing"],
        ["--check", "decision"],
        ["--check", "safety"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v538_read_only_final_review.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["read_only_final_review_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-read-only-final-review/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_READ_ONLY_FINAL_REVIEW.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5ReadOnlyFinalReviewStatus",
        "fetchV5ReadOnlyFinalReviewCharter",
        "fetchV5ReadOnlyFinalReviewRoles",
        "fetchV5ReadOnlyFinalReviewEvidence",
        "fetchV5ReadOnlyFinalReviewRisks",
        "fetchV5ReadOnlyFinalReviewMissingRequirements",
        "fetchV5ReadOnlyFinalReviewDecision",
        "fetchV5ReadOnlyFinalReviewAudit",
        "fetchV5ReadOnlyFinalReviewSafety",
        "fetchV5ReadOnlyFinalReviewSummary",
    ]:
        assert name in api_client
    assert "V5 Read-Only Final Review" in shell
    assert "Read-Only Final Review" in page
    assert "Final review only" in page
    assert "V5.38 Sandbox Read-Only Connector Final Review Board" in docs
    assert "scan_read_only_final_review_outputs" in scanner


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
        "final_review_runtime_enabled\": true",
        "final_review_passed\": true",
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

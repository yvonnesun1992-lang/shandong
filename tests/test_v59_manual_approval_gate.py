from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


SENSITIVE_TERMS = [
    "secret",
    "token",
    "password",
    "api_key",
    "authorization",
    "broker credential",
    "account_id",
    "real_order_id",
    "/users/apple",
]


def test_manual_approval_config_defaults_are_safe():
    from config.v5_manual_approval_config import get_manual_approval_status

    status = get_manual_approval_status()

    assert status["manual_approval_mode"] == "planned"
    assert status["manual_approval_required"] is True
    assert status["auto_approval_enabled"] is False
    assert status["real_order_after_approval"] is False
    assert status["real_orders_enabled"] is False
    assert status["paper_trading"] is True
    assert _is_safe(status)


def test_approval_request_model_contains_no_broker_credentials():
    from approval.approval_request import ApprovalRequest

    request = ApprovalRequest.create(
        order_intent_id="intent-1",
        symbol="AAPL",
        side="BUY",
        quantity=10,
        order_type="MARKET",
        notional_value=1750.0,
        signal_source="v5_alpha",
        signal_strength=0.7,
        risk_summary={"real_orders_enabled": False},
    )
    payload = request.as_dict()

    assert payload["approval_id"].startswith("approval-")
    assert payload["status"] == "DRAFT"
    assert "broker" not in json.dumps(payload).lower()
    assert _is_safe(payload)


def test_manual_approval_gate_rejects_or_requires_review_by_default():
    from approval.manual_approval_gate import ManualApprovalGate

    gate = ManualApprovalGate()
    request = gate.create_approval_request({"symbol": "AAPL", "side": "BUY", "quantity": 1, "order_type": "MARKET"}, {"real_orders_enabled": False})
    assert request.status == "PENDING_REVIEW"

    rejected = gate.reject_by_default({"symbol": "AAPL", "side": "BUY", "quantity": 1})
    reviewed = gate.review_approval_request(request.approval_id, decision="approve_simulated", reason="paper simulation review")
    summary = gate.approval_readiness_summary()

    assert rejected["status"] == "REJECTED"
    assert reviewed["status"] == "APPROVED_SIMULATED"
    assert reviewed["real_orders_enabled"] is False
    assert reviewed["real_order_after_approval"] is False
    assert summary["manual_approval_required"] is True
    assert summary["auto_approval_enabled"] is False
    assert summary["paper_trading"] is True
    assert _is_safe({"request": request.as_dict(), "rejected": rejected, "reviewed": reviewed, "summary": summary})


def test_approval_state_machine_blocks_live_or_auto_approval():
    from approval.approval_state_machine import ApprovalStateMachine

    machine = ApprovalStateMachine()

    assert machine.can_transition("DRAFT", "PENDING_REVIEW") is True
    assert machine.transition("DRAFT", "PENDING_REVIEW") == "PENDING_REVIEW"
    assert machine.can_transition("PENDING_REVIEW", "APPROVED_SIMULATED") is True
    assert machine.can_transition("PENDING_REVIEW", "REJECTED") is True
    assert machine.can_transition("PENDING_REVIEW", "EXPIRED") is True
    for blocked in ["AUTO_APPROVED", "LIVE_APPROVED", "REAL_ORDER_READY"]:
        assert machine.can_transition("PENDING_REVIEW", blocked) is False
        assert machine.transition("PENDING_REVIEW", blocked) == "REJECTED"
    assert machine.expire_if_timed_out("PENDING_REVIEW", age_seconds=999999, timeout_seconds=3600) == "EXPIRED"


def test_approval_audit_trail_writes_safe_jsonl(tmp_path):
    from approval.approval_audit_trail import ApprovalAuditTrail

    path = tmp_path / "manual_approval_audit.jsonl"
    trail = ApprovalAuditTrail(path=path)
    trail.record_approval_event("approval_created", approval_id="approval-1", metadata={"symbol": "AAPL"})
    trail.record_approval_event("real_order_attempt_rejected", approval_id="approval-1", metadata={"side": "BUY"})

    events = trail.get_approval_events()
    summary = trail.build_approval_audit_summary()

    assert len(events) == 2
    assert summary["event_count"] == 2
    assert summary["real_order_attempts_rejected"] == 1
    assert path.exists()
    assert _is_safe(events)
    assert _is_safe(path.read_text(encoding="utf-8"))


def test_approval_risk_summary_is_paper_only():
    from approval.approval_risk_summary import build_approval_risk_summary

    summary = build_approval_risk_summary({"symbol": "AAPL", "side": "BUY", "quantity": 5, "price": 100.0, "strength": 0.8})

    assert summary["symbol"] == "AAPL"
    assert summary["estimated_notional"] == 500.0
    assert summary["broker_connected"] is False
    assert summary["real_orders_enabled"] is False
    assert summary["real_money_enabled"] is False
    assert summary["paper_trading"] is True
    assert _is_safe(summary)


def test_approval_api_endpoints_return_safe_planning_payloads():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    for path in ["/api/v5/approval/status", "/api/v5/approval/readiness", "/api/v5/approval/policy", "/api/v5/approval/audit-summary"]:
        response = client.get(path)
        payload = response.json()

        assert response.status_code == 200
        assert payload["success"] is True
        encoded = json.dumps(payload).lower()
        assert "manual_approval_required" in encoded
        assert "auto_approval_enabled" in encoded
        assert "real_orders_enabled" in encoded
        assert "real_money_enabled" in encoded
        assert "paper_trading" in encoded
        assert _is_safe(payload)


def test_manual_approval_report_and_cli_can_run():
    from approval.manual_approval_report import generate_manual_approval_report

    result = generate_manual_approval_report()
    assert result["path"].endswith("reports/v5_9_manual_approval_gate_report.md")
    assert result["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(result)

    completed = subprocess.run(
        [sys.executable, "scripts/run_v59_manual_approval_gate.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode in {0, 1}
    payload = json.loads(completed.stdout)
    assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(payload)


def test_v59_frontend_helpers_navigation_docs_and_review_exist():
    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-approval/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5ApprovalStatus" in api_client
    assert "fetchV5ApprovalReadiness" in api_client
    assert "fetchV5ApprovalPolicy" in api_client
    assert "fetchV5ApprovalAuditSummary" in api_client
    assert "Manual Approval Gate Status" in page
    assert "Manual approval required: true" in page
    assert "Auto approval: disabled" in page
    assert "Real orders: disabled" in page
    assert "Real money: disabled" in page
    assert "Paper trading only" in page
    assert "Planning only" in page
    assert "V5 Approval" in shell
    assert "/v5-approval" in shell
    assert "V5.9" in _read("docs/V5_MANUAL_APPROVAL_GATE_PLANNING.md")
    assert "V5.9" in _read("README.md")
    assert "V5.9" in _read("REVIEW_PACKAGE.md")
    assert _is_safe(page)


def test_existing_v5_stack_tests_are_available():
    assert "test_paper_trading_runner_completes_closed_loop" in _read("tests/test_v50_paper_trading_core.py")
    assert "test_runtime_loop_runs_and_updates_portfolio" in _read("tests/test_v51_trading_engine_runtime.py")
    assert "test_engine_crash_recovery_logs_error" in _read("tests/test_v52_production_stability_engineering.py")
    assert "soak" in _read("tests/test_v53_long_run_soak_test.py").lower()
    assert "monitoring" in _read("tests/test_v54_live_paper_trading_monitoring_api.py").lower()
    assert "deployment" in _read("tests/test_v55_production_deployment_dry_run.py").lower()
    assert "live paper" in _read("tests/test_v56_live_paper_trading_staging.py").lower()
    assert "live alpha" in _read("tests/test_v57_live_alpha_signal_integration.py").lower()
    assert "broker integration" in _read("tests/test_v58_broker_integration_planning.py").lower()


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _is_safe(payload) -> bool:
    encoded = json.dumps(payload, default=str).lower()
    return not any(term in encoded for term in SENSITIVE_TERMS)

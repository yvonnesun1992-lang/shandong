from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "preflight_runtime_enabled",
    "packet_approval_enabled",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_preflight_packet_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_sandbox_preflight_packet_config import (
        get_preflight_packet_mode,
        get_preflight_packet_provider,
        get_preflight_packet_status,
    )

    assert get_preflight_packet_mode() == "preflight_packet_only"
    assert get_preflight_packet_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_preflight_packet_status()
    assert status["version"] == "V5.31"
    assert status["preflight_packet_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_PREFLIGHT_RUNTIME", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_PACKET_APPROVAL", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SECRET_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ACCOUNT_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_preflight_packet_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "preflight runtime requested but blocked in v5.31" in warnings
    assert "packet approval requested but blocked in v5.31" in warnings
    assert "sandbox api requested but blocked in v5.31" in warnings
    assert "secret read requested but blocked in v5.31" in warnings
    assert "account read requested but blocked in v5.31" in warnings
    assert "order submission requested but blocked in v5.31" in warnings
    assert "real money requested but blocked in v5.31" in warnings
    assert _is_safe(blocked)


def test_preflight_packet_components_decision_safety_and_orchestrator():
    from sandbox_preflight_packet.artifact_manifest import build_artifact_manifest, validate_artifact_manifest
    from sandbox_preflight_packet.blocking_item_register import build_blocking_item_register
    from sandbox_preflight_packet.final_decision_record import build_final_preflight_decision, evaluate_final_preflight_decision
    from sandbox_preflight_packet.final_preflight_checklist import build_final_preflight_checklist
    from sandbox_preflight_packet.preflight_audit_trail import build_preflight_audit_event, build_preflight_audit_trail
    from sandbox_preflight_packet.preflight_evidence_digest import build_preflight_evidence_digest
    from sandbox_preflight_packet.preflight_packet_orchestrator import build_preflight_packet, summarize_preflight_packet
    from sandbox_preflight_packet.preflight_safety_validator import build_preflight_safety_summary, validate_preflight_safety

    checklist = build_final_preflight_checklist("alpaca")
    manifest = build_artifact_manifest("alpaca")
    manifest_validation = validate_artifact_manifest(manifest)
    blocking = build_blocking_item_register("alpaca")
    digest = build_preflight_evidence_digest("alpaca")
    decision = build_final_preflight_decision("alpaca")
    simulated = evaluate_final_preflight_decision({"provider": "alpaca", "simulated_packet_approval": True})
    audit_event = build_preflight_audit_event("alpaca", "final_preflight")
    audit_trail = build_preflight_audit_trail("alpaca")
    safety = build_preflight_safety_summary()
    packet = build_preflight_packet("alpaca")
    summary = summarize_preflight_packet(packet)

    assert checklist["preflight_ready"] is False
    assert "review board decision is NO_GO" in [item["name"] for item in checklist["checks"]]
    assert manifest["artifacts"]
    assert manifest_validation["valid"] in {True, False}
    assert blocking["sandbox_dry_run_blocked"] is True
    assert blocking["blocking_count"] == len(blocking["blocking_items"])
    assert digest["evidence_digest_ready"] is False
    assert digest["final_decision"] == "NO_GO"
    assert decision["decision"] == "NO_GO"
    assert decision["sandbox_dry_run_allowed"] is False
    assert simulated["decision"] == "NO_GO"
    assert simulated["sandbox_dry_run_allowed"] is False
    assert audit_event["preflight_audit_id_placeholder"] == "PREFLIGHT_AUDIT_PLACEHOLDER"
    assert audit_event["raw_secret_logged"] is False
    assert audit_event["account_read"] is False
    assert audit_event["order_submitted"] is False
    assert audit_event["sandbox_api_called"] is False
    assert audit_trail["external_log_upload"] is False
    assert safety["safe"] is True
    assert validate_preflight_safety({"preflight_runtime_enabled": True})["safe"] is False
    assert validate_preflight_safety({"packet_approval_enabled": True})["safe"] is False
    assert validate_preflight_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_preflight_safety({"secret_read_enabled": True})["safe"] is False
    assert validate_preflight_safety({"account_read_enabled": True})["safe"] is False
    assert validate_preflight_safety({"order_submission_enabled": True})["safe"] is False
    assert validate_preflight_safety({"payload": "api_key=demo"})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    for item in [checklist, manifest, blocking, digest, decision, simulated, audit_event, audit_trail, safety, summary]:
        assert item["preflight_packet_only"] is True
        assert _is_safe(item)


def test_sandbox_preflight_packet_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/sandbox-preflight-packet/status",
        "/api/v5/sandbox-preflight-packet/checklist",
        "/api/v5/sandbox-preflight-packet/artifacts",
        "/api/v5/sandbox-preflight-packet/blocking-items",
        "/api/v5/sandbox-preflight-packet/evidence-digest",
        "/api/v5/sandbox-preflight-packet/decision",
        "/api/v5/sandbox-preflight-packet/audit",
        "/api/v5/sandbox-preflight-packet/safety",
        "/api/v5/sandbox-preflight-packet/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "preflight_packet_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from runtime.security_scan import scan_sandbox_preflight_packet_outputs
    from sandbox_preflight_packet.sandbox_preflight_packet_report import generate_sandbox_preflight_packet_report

    report = generate_sandbox_preflight_packet_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_31_sandbox_preflight_packet_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["preflight_packet_only"] is True
    assert scan_sandbox_preflight_packet_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "checklist"], ["--check", "artifacts"], ["--check", "decision"], ["--check", "safety"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v531_sandbox_preflight_packet.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["preflight_packet_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-sandbox-preflight-packet/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_SANDBOX_PREFLIGHT_PACKET.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5SandboxPreflightPacketStatus",
        "fetchV5SandboxPreflightPacketChecklist",
        "fetchV5SandboxPreflightPacketArtifacts",
        "fetchV5SandboxPreflightPacketBlockingItems",
        "fetchV5SandboxPreflightPacketEvidenceDigest",
        "fetchV5SandboxPreflightPacketDecision",
        "fetchV5SandboxPreflightPacketAudit",
        "fetchV5SandboxPreflightPacketSafety",
        "fetchV5SandboxPreflightPacketSummary",
    ]:
        assert name in api_client
    assert "V5 Preflight Packet" in shell
    assert "Sandbox Preflight Packet" in page
    assert "Final NO-GO Record" in page
    assert "V5.31 Sandbox Dry-Run Final Preflight Packet" in docs
    assert "scan_sandbox_preflight_packet_outputs" in scanner


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

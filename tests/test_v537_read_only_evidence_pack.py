from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "evidence_pack_runtime_enabled",
    "evidence_pack_passed",
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


def test_read_only_evidence_pack_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_read_only_evidence_pack_config import (
        get_read_only_evidence_pack_mode,
        get_read_only_evidence_pack_provider,
        get_read_only_evidence_pack_status,
    )

    assert get_read_only_evidence_pack_mode() == "read_only_evidence_pack_only"
    assert get_read_only_evidence_pack_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_read_only_evidence_pack_status()
    assert status["version"] == "V5.37"
    assert status["read_only_evidence_pack_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    for env_name in [
        "SHANDONG_V5_ENABLE_READ_ONLY_EVIDENCE_PACK_RUNTIME",
        "SHANDONG_V5_ENABLE_EVIDENCE_PACK_PASS",
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
    blocked = get_read_only_evidence_pack_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "evidence pack runtime requested but blocked in v5.37" in warnings
    assert "evidence pack pass requested but blocked in v5.37" in warnings
    assert "read-only connector requested but blocked in v5.37" in warnings
    assert "sandbox api requested but blocked in v5.37" in warnings
    assert "secret read requested but blocked in v5.37" in warnings
    assert "account read requested but blocked in v5.37" in warnings
    assert "position read requested but blocked in v5.37" in warnings
    assert "balance read requested but blocked in v5.37" in warnings
    assert "order preview requested but blocked in v5.37" in warnings
    assert "order submission requested but blocked in v5.37" in warnings
    assert "real money requested but blocked in v5.37" in warnings
    assert _is_safe(blocked)


def test_read_only_evidence_pack_mode_override_is_blocked(monkeypatch):
    from config.v5_read_only_evidence_pack_config import (
        get_read_only_evidence_pack_mode,
        get_read_only_evidence_pack_status,
    )

    monkeypatch.setenv("SHANDONG_V5_READ_ONLY_EVIDENCE_PACK_MODE", "production")
    status = get_read_only_evidence_pack_status()
    warnings = " | ".join(status["warnings"]).lower()

    assert get_read_only_evidence_pack_mode() == "read_only_evidence_pack_only"
    assert status["read_only_evidence_pack_mode"] == "read_only_evidence_pack_only"
    assert status["read_only_evidence_pack_only"] is True
    assert status["evidence_pack_passed"] is False
    assert status["read_only_connector_allowed"] is False
    assert "read-only evidence pack mode override requested but blocked in v5.37" in warnings
    for key in FALSE_KEYS:
        assert status[key] is False
    assert _is_safe(status)


def test_evidence_pack_modules_decision_orchestration_and_safety():
    from sandbox_read_only_evidence_pack.audit_evidence_pack import build_audit_evidence_pack
    from sandbox_read_only_evidence_pack.evidence_completeness_check import check_evidence_completeness
    from sandbox_read_only_evidence_pack.evidence_pack_decision import (
        build_evidence_pack_decision,
        evaluate_evidence_pack_decision,
    )
    from sandbox_read_only_evidence_pack.evidence_pack_orchestrator import (
        build_read_only_evidence_pack,
        summarize_read_only_evidence_pack,
    )
    from sandbox_read_only_evidence_pack.evidence_pack_safety_validator import (
        build_evidence_pack_safety_summary,
        validate_evidence_pack_safety,
    )
    from sandbox_read_only_evidence_pack.evidence_source_collector import (
        collect_evidence_sources,
        summarize_evidence_sources,
    )
    from sandbox_read_only_evidence_pack.order_blocking_evidence_pack import build_order_blocking_evidence_pack
    from sandbox_read_only_evidence_pack.redaction_evidence_pack import build_redaction_evidence_pack
    from sandbox_read_only_evidence_pack.safety_boundary_evidence_pack import build_safety_boundary_evidence_pack
    from sandbox_read_only_evidence_pack.schema_evidence_pack import build_schema_evidence_pack

    provider = "alpaca"
    sources = collect_evidence_sources(provider)
    source_summary = summarize_evidence_sources(sources)
    completeness = check_evidence_completeness(provider)
    redaction = build_redaction_evidence_pack(provider)
    schema = build_schema_evidence_pack(provider)
    audit = build_audit_evidence_pack(provider)
    order = build_order_blocking_evidence_pack(provider)
    safety_boundary = build_safety_boundary_evidence_pack(provider)
    decision = build_evidence_pack_decision(provider)
    evaluated = evaluate_evidence_pack_decision(
        {"evidence_complete": True, "stability_gate_passed": True, "simulated_approval": True}
    )
    safety = build_evidence_pack_safety_summary()
    pack = build_read_only_evidence_pack(provider)
    summary = summarize_read_only_evidence_pack(pack)

    assert sources["sources_collected"] is True
    assert sources["source_count"] >= 20
    assert source_summary["sources_collected"] is True
    assert completeness["evidence_complete"] is True
    assert redaction["redaction_evidence_ready"] is True
    assert schema["schema_evidence_ready"] is True
    assert audit["audit_evidence_ready"] is True
    assert order["order_blocking_evidence_ready"] is True
    assert order["order_submission_enabled"] is False
    assert safety_boundary["safety_evidence_ready"] is True
    for item in [decision, evaluated, summary]:
        assert item["decision"] == "READ_ONLY_EVIDENCE_ONLY"
        assert item["evidence_pack_passed"] is False
        assert item["read_only_connector_allowed"] is False
    assert safety["safe"] is True
    for key in FALSE_KEYS:
        assert validate_evidence_pack_safety({key: True})["safe"] is False
    assert validate_evidence_pack_safety({"payload": "MOCK_API_KEY_FOR_TEST_ONLY"})["safe"] is False
    assert validate_evidence_pack_safety({"cash_balance": 123})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    for item in [
        sources,
        source_summary,
        completeness,
        redaction,
        schema,
        audit,
        order,
        safety_boundary,
        decision,
        evaluated,
        safety,
        pack,
        summary,
    ]:
        assert item["read_only_evidence_pack_only"] is True
        assert _is_safe(item)


def test_read_only_evidence_pack_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/read-only-evidence-pack/status",
        "/api/v5/read-only-evidence-pack/sources",
        "/api/v5/read-only-evidence-pack/completeness",
        "/api/v5/read-only-evidence-pack/redaction",
        "/api/v5/read-only-evidence-pack/schema",
        "/api/v5/read-only-evidence-pack/audit",
        "/api/v5/read-only-evidence-pack/order-blocking",
        "/api/v5/read-only-evidence-pack/safety-boundary",
        "/api/v5/read-only-evidence-pack/decision",
        "/api/v5/read-only-evidence-pack/safety",
        "/api/v5/read-only-evidence-pack/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "read_only_evidence_pack_only" in text
        assert "paper_trading" in text
        assert "evidence_pack_passed" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from runtime.security_scan import scan_read_only_evidence_pack_outputs
    from sandbox_read_only_evidence_pack.sandbox_read_only_evidence_pack_report import (
        generate_sandbox_read_only_evidence_pack_report,
    )

    report = generate_sandbox_read_only_evidence_pack_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_37_sandbox_read_only_evidence_pack_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["read_only_evidence_pack_only"] is True
    assert scan_read_only_evidence_pack_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [
        [],
        ["--provider", "alpaca"],
        ["--provider", "ibkr"],
        ["--check", "sources"],
        ["--check", "completeness"],
        ["--check", "redaction"],
        ["--check", "schema"],
        ["--check", "order-blocking"],
        ["--check", "decision"],
        ["--check", "safety"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v537_read_only_evidence_pack.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["read_only_evidence_pack_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-read-only-evidence-pack/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_READ_ONLY_EVIDENCE_PACK.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5ReadOnlyEvidencePackStatus",
        "fetchV5ReadOnlyEvidencePackSources",
        "fetchV5ReadOnlyEvidencePackCompleteness",
        "fetchV5ReadOnlyEvidencePackRedaction",
        "fetchV5ReadOnlyEvidencePackSchema",
        "fetchV5ReadOnlyEvidencePackAudit",
        "fetchV5ReadOnlyEvidencePackOrderBlocking",
        "fetchV5ReadOnlyEvidencePackSafetyBoundary",
        "fetchV5ReadOnlyEvidencePackDecision",
        "fetchV5ReadOnlyEvidencePackSafety",
        "fetchV5ReadOnlyEvidencePackSummary",
    ]:
        assert name in api_client
    assert "V5 Read-Only Evidence Pack" in shell
    assert "Read-Only Evidence Pack" in page
    assert "Evidence pack only" in page
    assert "V5.37 Sandbox Read-Only Connector Evidence Pack" in docs
    assert "scan_read_only_evidence_pack_outputs" in scanner


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
        "evidence_pack_runtime_enabled\": true",
        "evidence_pack_passed\": true",
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

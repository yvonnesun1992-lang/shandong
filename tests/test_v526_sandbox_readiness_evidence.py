from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}
FALSE_KEYS = [
    "evidence_runtime_enabled",
    "sandbox_api_enabled",
    "account_read_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_evidence_config_defaults_and_blocks_real_path_env(monkeypatch):
    from config.v5_sandbox_readiness_evidence_config import get_evidence_mode, get_evidence_provider, get_evidence_status

    assert get_evidence_mode() == "evidence_only"
    assert get_evidence_provider() in PROVIDERS
    status = get_evidence_status()
    assert status["version"] == "V5.26"
    assert status["evidence_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_EVIDENCE_RUNTIME", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ACCOUNT_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_evidence_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "evidence runtime requested but blocked in v5.26" in warnings
    assert "sandbox api requested but blocked in v5.26" in warnings
    assert "account read requested but blocked in v5.26" in warnings
    assert "order submission requested but blocked in v5.26" in warnings
    assert "real money requested but blocked in v5.26" in warnings
    assert _is_safe(blocked)


def test_evidence_sources_summaries_gaps_gate_and_safety():
    from provider_sandbox_evidence.evidence_orchestrator import build_sandbox_readiness_evidence_pack, summarize_evidence_pack
    from provider_sandbox_evidence.evidence_safety_validator import build_evidence_safety_summary, validate_evidence_safety
    from provider_sandbox_evidence.evidence_source_collector import collect_evidence_sources, summarize_evidence_sources
    from provider_sandbox_evidence.fault_evidence_summary import build_fault_evidence_summary
    from provider_sandbox_evidence.readiness_gap_analyzer import analyze_readiness_gaps
    from provider_sandbox_evidence.replay_evidence_summary import build_replay_evidence_summary
    from provider_sandbox_evidence.sandbox_entry_gate import build_sandbox_entry_gate_summary, evaluate_sandbox_entry_gate
    from provider_sandbox_evidence.soak_evidence_summary import build_soak_evidence_summary

    sources = collect_evidence_sources("alpaca")
    source_summary = summarize_evidence_sources("alpaca")
    replay = build_replay_evidence_summary("alpaca")
    fault = build_fault_evidence_summary("alpaca")
    soak = build_soak_evidence_summary("alpaca")
    gaps = analyze_readiness_gaps("alpaca")
    gate = evaluate_sandbox_entry_gate("alpaca")
    gate_summary = build_sandbox_entry_gate_summary("alpaca")
    safety = build_evidence_safety_summary()
    pack = build_sandbox_readiness_evidence_pack("alpaca")
    summary = summarize_evidence_pack(pack)

    assert sources["evidence_only"] is True
    assert {"v5_23_offline_replay", "v5_24_fault_injection", "v5_25_offline_soak"} <= set(sources["sources"])
    assert source_summary["total_sources"] == 3
    assert replay["evidence_only"] is True
    assert fault["evidence_only"] is True
    assert soak["evidence_only"] is True
    assert gaps["ready_for_sandbox_api"] is False
    assert gaps["ready_for_sandbox_orders"] is False
    assert "credential vault not implemented" in gaps["blocking_gaps"]
    assert gate["gate"] == "BLOCKED"
    assert gate["ready_for_sandbox_api"] is False
    assert gate_summary["gate"] == "BLOCKED"
    assert safety["safe"] is True
    assert validate_evidence_safety({"evidence_runtime_enabled": True})["safe"] is False
    assert validate_evidence_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_evidence_safety({"account_read_enabled": True})["safe"] is False
    assert validate_evidence_safety({"order_submission_enabled": True})["safe"] is False
    assert validate_evidence_safety({"payload": "token=demo"})["safe"] is False
    assert validate_evidence_safety({"payload": "raw provider payload"})["safe"] is False
    assert validate_evidence_safety({"payload": "https://paper-api.alpaca.markets"})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    for item in [sources, source_summary, replay, fault, soak, gaps, gate, gate_summary, safety, summary]:
        assert item["evidence_only"] is True
        assert _is_safe(item)


def test_sandbox_evidence_api_endpoints_return_safe_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/sandbox-evidence/status",
        "/api/v5/sandbox-evidence/sources",
        "/api/v5/sandbox-evidence/replay",
        "/api/v5/sandbox-evidence/fault",
        "/api/v5/sandbox-evidence/soak",
        "/api/v5/sandbox-evidence/gaps",
        "/api/v5/sandbox-evidence/gate",
        "/api/v5/sandbox-evidence/safety",
        "/api/v5/sandbox-evidence/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "evidence_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from provider_sandbox_evidence.provider_sandbox_evidence_report import generate_sandbox_readiness_evidence_report
    from runtime.security_scan import scan_sandbox_evidence_outputs

    report = generate_sandbox_readiness_evidence_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_26_sandbox_readiness_evidence_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["evidence_only"] is True
    assert scan_sandbox_evidence_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "gate"], ["--check", "safety"], ["--check", "gaps"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v526_sandbox_readiness_evidence.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["evidence_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-sandbox-evidence/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_SANDBOX_READINESS_EVIDENCE.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5SandboxEvidenceStatus",
        "fetchV5SandboxEvidenceSources",
        "fetchV5SandboxEvidenceReplay",
        "fetchV5SandboxEvidenceFault",
        "fetchV5SandboxEvidenceSoak",
        "fetchV5SandboxEvidenceGaps",
        "fetchV5SandboxEvidenceGate",
        "fetchV5SandboxEvidenceSafety",
        "fetchV5SandboxEvidenceSummary",
    ]:
        assert name in api_client
    assert "V5 Sandbox Evidence" in shell
    assert "Sandbox Evidence Status" in page
    assert "Sandbox Entry Gate" in page
    assert "V5.26 Provider Sandbox Readiness Evidence Pack" in docs
    assert "scan_sandbox_evidence_outputs" in scanner


def test_all_previous_v5_test_files_exist_through_v525():
    for version in [
        "v523_provider_offline_replay",
        "v524_provider_fault_injection",
        "v525_provider_offline_soak",
    ]:
        assert Path(f"tests/test_{version}.py").exists()


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

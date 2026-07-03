from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "local_e2e_runtime_enabled",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "balance_read_enabled",
    "position_read_enabled",
    "order_preview_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_local_e2e_config_defaults_and_blocks_env(monkeypatch):
    from config.v5_local_e2e_config import get_local_e2e_mode, get_local_e2e_status

    status = get_local_e2e_status()
    assert get_local_e2e_mode() == "local_e2e_verification_only"
    assert status["local_e2e_mode"] == "local_e2e_verification_only"
    assert status["local_e2e_verification_only"] is True
    assert status["localhost_only"] is True
    assert status["backend_start_allowed"] is True
    assert status["frontend_start_allowed"] is True
    assert status["browser_check_allowed"] is True
    assert status["api_smoke_test_allowed"] is True
    assert status["log_write_test_allowed"] is True
    assert status["report_generation_allowed"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_LOCAL_E2E_MODE", "production")
    for env_name in [
        "SHANDONG_V5_ENABLE_LOCAL_E2E_RUNTIME",
        "SHANDONG_V5_ENABLE_SANDBOX_API",
        "SHANDONG_V5_ENABLE_SECRET_READ",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION",
        "SHANDONG_V5_ENABLE_REAL_MONEY",
    ]:
        monkeypatch.setenv(env_name, "true")
    blocked = get_local_e2e_status()
    warnings = " | ".join(blocked["warnings"]).lower()
    assert get_local_e2e_mode() == "local_e2e_verification_only"
    assert blocked["local_e2e_mode"] == "local_e2e_verification_only"
    assert "mode override requested but blocked in v5.41" in warnings
    assert "sandbox api requested but blocked in v5.41" in warnings
    assert "secret read requested but blocked in v5.41" in warnings
    assert "account read requested but blocked in v5.41" in warnings
    assert "order submission requested but blocked in v5.41" in warnings
    assert "real money requested but blocked in v5.41" in warnings
    for key in FALSE_KEYS:
        assert blocked[key] is False
    assert _safe_payload(blocked)


def test_local_e2e_modules_orchestrator_report_and_safety():
    from local_e2e_verification.api_smoke_test_matrix import build_api_smoke_test_matrix, run_api_smoke_tests, summarize_api_smoke_tests
    from local_e2e_verification.backend_smoke_test import build_backend_smoke_test_plan, run_backend_smoke_test, summarize_backend_smoke_test
    from local_e2e_verification.frontend_smoke_test import build_frontend_smoke_test_plan, summarize_frontend_smoke_test, verify_frontend_files
    from local_e2e_verification.init import boundary
    from local_e2e_verification.local_e2e_orchestrator import run_local_e2e_verification, summarize_local_e2e_verification
    from local_e2e_verification.local_launcher_verification import (
        summarize_local_launcher_verification,
        verify_local_launcher_plan,
        verify_local_launcher_scripts,
    )
    from local_e2e_verification.log_write_verification import summarize_log_verification, verify_log_read, verify_log_write
    from local_e2e_verification.report_generation_verification import (
        generate_local_e2e_verification_report,
        summarize_report_generation,
    )
    from local_e2e_verification.safety_boundary_verification import build_local_e2e_safety_summary, verify_local_e2e_safety
    from runtime.security_scan import scan_local_e2e_outputs

    assert boundary()["local_e2e_verification_only"] is True
    launcher = verify_local_launcher_plan()
    scripts = verify_local_launcher_scripts()
    launcher_summary = summarize_local_launcher_verification({"plan": launcher, "scripts": scripts})
    backend = run_backend_smoke_test()
    frontend = verify_frontend_files()
    api = run_api_smoke_tests()
    log_write = verify_log_write()
    log_read = verify_log_read()
    report = generate_local_e2e_verification_report()
    safety = build_local_e2e_safety_summary()
    orchestrated = run_local_e2e_verification()
    summary = summarize_local_e2e_verification(orchestrated)

    assert build_backend_smoke_test_plan()["dry_run"] is True
    assert build_frontend_smoke_test_plan()["dry_run"] is True
    assert build_api_smoke_test_matrix()["endpoint_count"] >= 12
    assert launcher["local_launcher_verified"] is True
    assert scripts["local_launcher_scripts_verified"] is True
    assert launcher_summary["local_launcher_verified"] is True
    assert backend["backend_smoke_passed"] is True
    assert summarize_backend_smoke_test(backend)["backend_smoke_passed"] is True
    assert frontend["frontend_smoke_passed"] is True
    assert summarize_frontend_smoke_test(frontend)["frontend_smoke_passed"] is True
    assert api["api_smoke_passed"] is True
    assert summarize_api_smoke_tests(api)["api_smoke_passed"] is True
    assert log_write["log_write_passed"] is True
    assert log_read["log_read_passed"] is True
    assert summarize_log_verification({"write": log_write, "read": log_read})["log_write_passed"] is True
    assert report["report_generated"] is True
    assert summarize_report_generation(report)["report_generated"] is True
    assert safety["safe"] is True
    assert verify_local_e2e_safety({"sandbox_api_enabled": True})["safe"] is False
    assert verify_local_e2e_safety({"target": "https://example.com"})["safe"] is False
    assert verify_local_e2e_safety({"payload": "raw provider payload"})["safe"] is False
    assert orchestrated["local_e2e_ready"] is True
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert report["path"].endswith("reports/v5_41_local_e2e_verification_report.md")
    assert scan_local_e2e_outputs(report)["safe"] is True
    for payload in [launcher, scripts, launcher_summary, backend, frontend, api, log_write, log_read, report, safety, orchestrated, summary]:
        assert _safe_payload(payload)


def test_local_e2e_api_endpoints_return_locked_flags():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/local-e2e/status",
        "/api/v5/local-e2e/launcher",
        "/api/v5/local-e2e/backend",
        "/api/v5/local-e2e/frontend",
        "/api/v5/local-e2e/api-smoke",
        "/api/v5/local-e2e/logs",
        "/api/v5/local-e2e/report",
        "/api/v5/local-e2e/safety",
        "/api/v5/local-e2e/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "local_e2e_verification_only" in text
        assert "localhost_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _safe_payload(payload)


def test_cli_frontend_docs_navigation_and_security_scan_are_present():
    for args in [
        [],
        ["--check", "launcher"],
        ["--check", "backend"],
        ["--check", "frontend"],
        ["--check", "api"],
        ["--check", "logs"],
        ["--check", "report"],
        ["--check", "safety"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v541_local_e2e_verification.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["local_e2e_verification_only"] is True
        assert _safe_payload(payload)

    page = Path("web/frontend/app/v5-local-e2e/page.tsx").read_text(encoding="utf-8")
    api_client = Path("web/frontend/app/lib/apiClient.ts").read_text(encoding="utf-8")
    shell = Path("web/frontend/app/components/ProductionShell.tsx").read_text(encoding="utf-8")
    docs = Path("docs/V5_LOCAL_E2E_VERIFICATION.md").read_text(encoding="utf-8")
    scanner = Path("runtime/security_scan.py").read_text(encoding="utf-8")
    assert "Local E2E Verification" in page
    assert "It does not connect to brokers" in page
    assert "It does not submit orders" in page
    assert "It does not use real money" in page
    assert "fetchV5LocalE2ESummary" in api_client
    assert "fetchV5LocalE2EApiSmoke" in api_client
    assert "V5 Local E2E" in shell
    assert "V5.41 Local End-to-End Run Verification" in docs
    assert "scan_local_e2e_outputs" in scanner
    assert _safe_text(page + api_client + shell + docs)


def _safe_payload(payload: object) -> bool:
    return _safe_text(json.dumps(payload, default=str).lower())


def _safe_text(text: str) -> bool:
    lowered = text.lower()
    blocked = [
        "api_key=demo",
        "secret_value=demo",
        "token=demo",
        "password=demo",
        "authorization: bearer",
        "real_order_id_",
        "real_account_id",
        "raw provider payload",
        "paper-api.",
        "api.alpaca.",
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "sandbox_api_enabled\": true",
        "secret_read_enabled\": true",
        "account_read_enabled\": true",
        "balance_read_enabled\": true",
        "position_read_enabled\": true",
        "order_submission_enabled\": true",
        "broker_connected\": true",
        "real_money_enabled\": true",
    ]
    return not any(term in lowered for term in blocked)

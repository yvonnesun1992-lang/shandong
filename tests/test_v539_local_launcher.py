from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


LOCKED_FALSE_KEYS = [
    "local_launcher_runtime_enabled",
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


def test_local_launcher_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_local_launcher_config import (
        get_local_backend_url,
        get_local_frontend_url,
        get_local_launcher_mode,
        get_local_launcher_status,
    )

    status = get_local_launcher_status()
    assert get_local_launcher_mode() == "local_launcher_only"
    assert status["local_launcher_mode"] == "local_launcher_only"
    assert status["local_launcher_only"] is True
    assert status["localhost_only"] is True
    assert status["backend_launch_allowed"] is True
    assert status["frontend_launch_allowed"] is True
    assert status["browser_open_allowed"] is True
    assert status["paper_trading"] is True
    for key in LOCKED_FALSE_KEYS:
        assert status[key] is False
    assert get_local_backend_url().startswith("http://127.0.0.1:")
    assert get_local_frontend_url().startswith("http://127.0.0.1:")

    monkeypatch.setenv("SHANDONG_V5_LOCAL_LAUNCHER_MODE", "production")
    monkeypatch.setenv("SHANDONG_V5_BACKEND_HOST", "example.com")
    monkeypatch.setenv("SHANDONG_V5_FRONTEND_HOST", "0.0.0.0")
    for env_name in [
        "SHANDONG_V5_ENABLE_LOCAL_LAUNCHER_RUNTIME",
        "SHANDONG_V5_ENABLE_SANDBOX_API",
        "SHANDONG_V5_ENABLE_SECRET_READ",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION",
        "SHANDONG_V5_ENABLE_REAL_MONEY",
    ]:
        monkeypatch.setenv(env_name, "true")
    blocked = get_local_launcher_status()
    warnings = " | ".join(blocked["warnings"]).lower()
    assert get_local_launcher_mode() == "local_launcher_only"
    assert blocked["local_launcher_mode"] == "local_launcher_only"
    assert "mode override requested but blocked in v5.39" in warnings
    assert "backend host override requested but forced to localhost" in warnings
    assert "frontend host override requested but forced to localhost" in warnings
    assert "sandbox api requested but blocked in v5.39" in warnings
    assert "secret read requested but blocked in v5.39" in warnings
    assert "account read requested but blocked in v5.39" in warnings
    assert "order submission requested but blocked in v5.39" in warnings
    assert "real money requested but blocked in v5.39" in warnings
    for key in LOCKED_FALSE_KEYS:
        assert blocked[key] is False
    assert _safe_payload(blocked)


def test_local_launcher_modules_plan_logs_and_safety(tmp_path, monkeypatch):
    from local_launcher.backend_launcher import build_backend_command, launch_backend
    from local_launcher.browser_opener import build_browser_open_target, open_browser
    from local_launcher.environment_checker import run_environment_check
    from local_launcher.frontend_launcher import build_frontend_command, launch_frontend
    from local_launcher.init import boundary
    from local_launcher.launcher_log_manager import read_recent_launcher_logs, write_launcher_log
    from local_launcher.local_launcher_orchestrator import build_local_launcher_plan, run_local_launcher
    from local_launcher.local_launcher_safety_validator import (
        build_local_launcher_safety_summary,
        validate_local_launcher_safety,
    )
    from local_launcher.port_checker import check_launcher_ports, suggest_alternative_ports

    monkeypatch.setenv("SHANDONG_V5_BACKEND_HOST", "example.com")
    monkeypatch.setenv("SHANDONG_V5_FRONTEND_HOST", "example.com")

    env = run_environment_check()
    ports = check_launcher_ports()
    backend_command = build_backend_command()
    frontend_command = build_frontend_command()
    browser_target = build_browser_open_target()
    plan = build_local_launcher_plan()
    result = run_local_launcher()

    assert boundary()["local_launcher_only"] is True
    assert env["local_launcher_only"] is True
    assert "src/api/v2/server.py" in json.dumps(env)
    assert ports["localhost_only"] is True
    assert suggest_alternative_ports("127.0.0.1", 8000, count=1)
    assert "127.0.0.1" in backend_command
    assert "uvicorn" in " ".join(backend_command)
    assert "127.0.0.1" in frontend_command
    assert "pnpm" in " ".join(frontend_command)
    assert browser_target == "http://127.0.0.1:3000"
    assert launch_backend()["dry_run"] is True
    assert launch_frontend()["dry_run"] is True
    assert open_browser()["dry_run"] is True
    assert plan["dry_run"] is True
    assert result["dry_run"] is True
    assert result["local_launcher_only"] is True
    assert result["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert build_local_launcher_safety_summary()["safe"] is True
    assert validate_local_launcher_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_local_launcher_safety({"browser_target": "https://example.com"})["safe"] is False
    assert validate_local_launcher_safety({"payload": "raw provider payload"})["safe"] is False
    assert validate_local_launcher_safety({"payload": "real_order_id_123"})["safe"] is False

    monkeypatch.setenv("SHANDONG_V5_LOCAL_LAUNCHER_LOG_DIR", str(tmp_path))
    event = write_launcher_log({"action": "start", "status": "ok", "details": {"token": "demo", "account_id": "abc"}})
    assert "token" not in json.dumps(event).lower()
    assert "account_id" not in json.dumps(event).lower()
    logs = read_recent_launcher_logs()
    assert logs and _safe_payload(logs)


def test_local_launcher_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/local-launcher/status",
        "/api/v5/local-launcher/environment",
        "/api/v5/local-launcher/ports",
        "/api/v5/local-launcher/backend",
        "/api/v5/local-launcher/frontend",
        "/api/v5/local-launcher/browser",
        "/api/v5/local-launcher/logs",
        "/api/v5/local-launcher/safety",
        "/api/v5/local-launcher/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "local_launcher_only" in text
        assert "localhost_only" in text
        assert "paper_trading" in text
        for key in LOCKED_FALSE_KEYS:
            assert key in text
        assert _safe_payload(payload)


def test_cli_report_frontend_scripts_docs_and_security_scan_are_present():
    from local_launcher.local_launcher_report import generate_local_launcher_report
    from runtime.security_scan import scan_local_launcher_outputs

    for args in [
        [],
        ["--check", "environment"],
        ["--check", "ports"],
        ["--check", "backend"],
        ["--check", "frontend"],
        ["--check", "browser"],
        ["--check", "safety"],
        ["--dry-run"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v539_local_launcher.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["local_launcher_only"] is True
        assert _safe_payload(payload)

    report = generate_local_launcher_report()
    assert report["path"].endswith("reports/v5_39_local_launcher_report.md")
    assert report["local_launcher_only"] is True
    assert scan_local_launcher_outputs(report)["safe"] is True
    assert _safe_payload(report)

    assert Path("scripts/start_shandong_mac.command").exists()
    assert Path("scripts/start_shandong_windows.bat").exists()
    assert Path("web/frontend/app/v5-local-launcher/page.tsx").exists()
    assert Path("docs/V5_LOCAL_DESKTOP_LAUNCHER.md").exists()
    api_client = Path("web/frontend/app/lib/apiClient.ts").read_text(encoding="utf-8")
    shell = Path("web/frontend/app/components/ProductionShell.tsx").read_text(encoding="utf-8")
    page = Path("web/frontend/app/v5-local-launcher/page.tsx").read_text(encoding="utf-8")
    scanner = Path("runtime/security_scan.py").read_text(encoding="utf-8")
    assert "fetchV5LocalLauncherStatus" in api_client
    assert "V5 Local Launcher" in shell
    assert "Mac users" in page
    assert "Windows users" in page
    assert "scan_local_launcher_outputs" in scanner
    assert _safe_text(api_client + shell + page)


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
        "ibkr",
        "alpaca_trade_api",
        "ib_insync",
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

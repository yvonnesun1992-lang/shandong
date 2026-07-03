from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "doctor_runtime_enabled",
    "auto_fix_enabled",
    "install_dependencies_enabled",
    "external_network_enabled",
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


def test_local_run_doctor_config_defaults_and_blocks_env(monkeypatch):
    from config.v5_local_run_doctor_config import get_local_run_doctor_mode, get_local_run_doctor_status

    status = get_local_run_doctor_status()
    assert get_local_run_doctor_mode() == "local_run_doctor_only"
    assert status["local_run_doctor_mode"] == "local_run_doctor_only"
    assert status["local_run_doctor_only"] is True
    assert status["localhost_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_LOCAL_RUN_DOCTOR_MODE", "production")
    for env_name in [
        "SHANDONG_V5_ENABLE_LOCAL_RUN_DOCTOR_RUNTIME",
        "SHANDONG_V5_ENABLE_AUTO_FIX",
        "SHANDONG_V5_ENABLE_INSTALL_DEPENDENCIES",
        "SHANDONG_V5_ENABLE_EXTERNAL_NETWORK",
        "SHANDONG_V5_ENABLE_SANDBOX_API",
        "SHANDONG_V5_ENABLE_SECRET_READ",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION",
        "SHANDONG_V5_ENABLE_REAL_MONEY",
    ]:
        monkeypatch.setenv(env_name, "true")
    blocked = get_local_run_doctor_status()
    warnings = " | ".join(blocked["warnings"]).lower()
    assert get_local_run_doctor_mode() == "local_run_doctor_only"
    assert blocked["local_run_doctor_mode"] == "local_run_doctor_only"
    assert "mode override requested but blocked in v5.42" in warnings
    assert "auto fix requested but blocked in v5.42" in warnings
    assert "install dependencies requested but blocked in v5.42" in warnings
    assert "external network requested but blocked in v5.42" in warnings
    assert "sandbox api requested but blocked in v5.42" in warnings
    assert "secret read requested but blocked in v5.42" in warnings
    assert "account read requested but blocked in v5.42" in warnings
    assert "order submission requested but blocked in v5.42" in warnings
    assert "real money requested but blocked in v5.42" in warnings
    for key in FALSE_KEYS:
        assert blocked[key] is False
    assert _safe_payload(blocked)


def test_local_run_doctor_modules_report_and_safety():
    from local_run_doctor.backend_diagnosis import (
        build_backend_start_command,
        diagnose_backend_import,
        diagnose_backend_status_endpoint,
        diagnose_backend_testclient,
        summarize_backend_diagnosis,
    )
    from local_run_doctor.browser_diagnosis import build_backend_status_url, build_frontend_url, diagnose_browser_targets
    from local_run_doctor.command_availability_doctor import (
        check_command_available,
        check_python_available,
        run_command_availability_doctor,
    )
    from local_run_doctor.frontend_diagnosis import (
        build_frontend_install_command,
        build_frontend_start_command,
        diagnose_frontend_files,
        diagnose_frontend_node_modules,
        diagnose_frontend_package_json,
        summarize_frontend_diagnosis,
    )
    from local_run_doctor.human_friendly_fix_guide import build_fix_guide, build_mac_fix_guide, build_windows_fix_guide
    from local_run_doctor.init import boundary
    from local_run_doctor.local_run_doctor_orchestrator import run_local_run_doctor, summarize_local_run_doctor
    from local_run_doctor.local_run_doctor_report import generate_local_run_doctor_report, summarize_local_run_doctor_report
    from local_run_doctor.local_run_doctor_safety_validator import (
        build_local_run_doctor_safety_summary,
        validate_local_run_doctor_safety,
    )
    from local_run_doctor.port_diagnosis import check_local_port, diagnose_default_ports, suggest_port_fix
    from runtime.security_scan import scan_local_run_doctor_outputs

    assert boundary()["local_run_doctor_only"] is True
    assert check_command_available("python")["command"] == "python"
    assert isinstance(check_python_available()["python_available"], bool)
    commands = run_command_availability_doctor()
    ports = diagnose_default_ports()
    backend_import = diagnose_backend_import()
    backend_client = diagnose_backend_testclient()
    backend_status = diagnose_backend_status_endpoint()
    backend = summarize_backend_diagnosis()
    frontend_files = diagnose_frontend_files()
    frontend_package = diagnose_frontend_package_json()
    frontend_modules = diagnose_frontend_node_modules()
    frontend = summarize_frontend_diagnosis()
    browser = diagnose_browser_targets()
    doctor = run_local_run_doctor()
    summary = summarize_local_run_doctor(doctor)
    guide = build_fix_guide(doctor)
    report = generate_local_run_doctor_report()
    safety = build_local_run_doctor_safety_summary()

    assert check_local_port("127.0.0.1", 3000)["localhost_only"] is True
    assert ports["frontend_port"] == 3000
    assert ports["backend_port"] == 8000
    assert suggest_port_fix(ports)["suggestions"]
    assert backend_import["backend_import_ok"] is True
    assert backend_client["backend_testclient_ok"] is True
    assert backend_status["product_home_status_ok"] is True
    assert backend_status["local_launcher_status_ok"] is True
    assert "127.0.0.1" in build_backend_start_command()
    assert backend["backend_ready"] is True
    assert frontend_files["home_page_productized"] is True
    assert frontend_package["package_json_exists"] is True
    assert isinstance(frontend_modules["node_modules_exists"], bool)
    assert build_frontend_install_command() == "cd web/frontend && pnpm install"
    assert "127.0.0.1" in build_frontend_start_command()
    assert "3000" in build_frontend_start_command()
    assert frontend["frontend_ready"] is True
    assert build_frontend_url() == "http://127.0.0.1:3000"
    assert build_backend_status_url() == "http://127.0.0.1:8000/api/v5/product-home/status"
    assert browser["browser_targets_valid"] is True
    assert "likely_reason_3000_not_open" in doctor
    assert doctor["verdict"] in {"PASS", "WARNING"}
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert guide["recommended_next_steps"]
    assert "Mac" in "\n".join(build_mac_fix_guide(doctor))
    assert "Windows" in "\n".join(build_windows_fix_guide(doctor))
    assert report["report_generated"] is True
    assert summarize_local_run_doctor_report(report)["report_generated"] is True
    assert safety["safe"] is True
    assert validate_local_run_doctor_safety({"target": "https://example.com"})["safe"] is False
    assert validate_local_run_doctor_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_local_run_doctor_safety({"payload": "raw provider payload"})["safe"] is False
    assert report["path"].endswith("reports/v5_42_local_run_doctor_report.md")
    assert scan_local_run_doctor_outputs(report)["safe"] is True
    for payload in [commands, ports, backend, frontend, browser, doctor, summary, guide, report, safety]:
        assert _safe_payload(payload)


def test_local_run_doctor_api_endpoints_return_locked_flags():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/local-run-doctor/status",
        "/api/v5/local-run-doctor/commands",
        "/api/v5/local-run-doctor/ports",
        "/api/v5/local-run-doctor/backend",
        "/api/v5/local-run-doctor/frontend",
        "/api/v5/local-run-doctor/browser",
        "/api/v5/local-run-doctor/fix-guide",
        "/api/v5/local-run-doctor/safety",
        "/api/v5/local-run-doctor/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "local_run_doctor_only" in text
        assert "localhost_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _safe_payload(payload)


def test_cli_frontend_docs_navigation_and_security_scan_are_present():
    for args in [
        [],
        ["--check", "commands"],
        ["--check", "ports"],
        ["--check", "backend"],
        ["--check", "frontend"],
        ["--check", "browser"],
        ["--check", "fix-guide"],
        ["--check", "safety"],
        ["--check", "report"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v542_local_run_doctor.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["local_run_doctor_only"] is True
        assert _safe_payload(payload)

    page = Path("web/frontend/app/v5-local-run-doctor/page.tsx").read_text(encoding="utf-8")
    api_client = Path("web/frontend/app/lib/apiClient.ts").read_text(encoding="utf-8")
    shell = Path("web/frontend/app/components/ProductionShell.tsx").read_text(encoding="utf-8")
    docs = Path("docs/V5_LOCAL_RUN_DOCTOR.md").read_text(encoding="utf-8")
    scanner = Path("runtime/security_scan.py").read_text(encoding="utf-8")
    assert "Local Run Doctor" in page
    assert "Why 127.0.0.1:3000 may not open" in page
    assert "This doctor does not install anything automatically" in page
    assert "It does not connect to brokers" in page
    assert "It does not submit orders" in page
    assert "It does not use real money" in page
    assert "fetchV5LocalRunDoctorSummary" in api_client
    assert "fetchV5LocalRunDoctorFixGuide" in api_client
    assert "V5 Local Run Doctor" in shell
    assert "V5.42 Local Run Doctor" in docs
    assert "scan_local_run_doctor_outputs" in scanner
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
        "auto_fix_enabled\": true",
        "install_dependencies_enabled\": true",
        "external_network_enabled\": true",
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

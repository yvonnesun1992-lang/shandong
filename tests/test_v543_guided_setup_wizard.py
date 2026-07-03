from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "guided_setup_runtime_enabled",
    "auto_install_enabled",
    "external_network_enabled",
    "system_path_modify_enabled",
    "admin_permission_required",
    "long_running_process_start_enabled",
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


def test_guided_setup_config_defaults_and_blocks_env(monkeypatch):
    from config.v5_guided_setup_config import get_guided_setup_mode, get_guided_setup_status

    status = get_guided_setup_status()
    assert get_guided_setup_mode() == "guided_setup_only"
    assert status["guided_setup_mode"] == "guided_setup_only"
    assert status["guided_setup_only"] is True
    assert status["localhost_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_GUIDED_SETUP_MODE", "production")
    for env_name in [
        "SHANDONG_V5_ENABLE_GUIDED_SETUP_RUNTIME",
        "SHANDONG_V5_ENABLE_AUTO_INSTALL",
        "SHANDONG_V5_ENABLE_EXTERNAL_NETWORK",
        "SHANDONG_V5_ENABLE_SYSTEM_PATH_MODIFY",
        "SHANDONG_V5_ENABLE_ADMIN_PERMISSION",
        "SHANDONG_V5_ENABLE_LONG_RUNNING_PROCESS_START",
        "SHANDONG_V5_ENABLE_SANDBOX_API",
        "SHANDONG_V5_ENABLE_SECRET_READ",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION",
        "SHANDONG_V5_ENABLE_REAL_MONEY",
    ]:
        monkeypatch.setenv(env_name, "true")
    blocked = get_guided_setup_status()
    warnings = " | ".join(blocked["warnings"]).lower()
    assert get_guided_setup_mode() == "guided_setup_only"
    assert blocked["guided_setup_mode"] == "guided_setup_only"
    assert "mode override requested but blocked in v5.43" in warnings
    assert "auto install requested but blocked in v5.43" in warnings
    assert "external network requested but blocked in v5.43" in warnings
    assert "system path modify requested but blocked in v5.43" in warnings
    assert "admin permission requested but blocked in v5.43" in warnings
    assert "long running process start requested but blocked in v5.43" in warnings
    assert "sandbox api requested but blocked in v5.43" in warnings
    assert "secret read requested but blocked in v5.43" in warnings
    assert "account read requested but blocked in v5.43" in warnings
    assert "order submission requested but blocked in v5.43" in warnings
    assert "real money requested but blocked in v5.43" in warnings
    for key in FALSE_KEYS:
        assert blocked[key] is False
    assert _safe_payload(blocked)


def test_guided_setup_modules_report_and_safety():
    from guided_setup.command_copy_blocks import build_command_copy_blocks, build_mac_command_blocks, build_windows_command_blocks
    from guided_setup.guided_setup_orchestrator import build_guided_setup_wizard, summarize_guided_setup_wizard
    from guided_setup.guided_setup_report import generate_guided_setup_report, summarize_guided_setup_report
    from guided_setup.guided_setup_safety_validator import build_guided_setup_safety_summary, validate_guided_setup_safety
    from guided_setup.init import boundary
    from guided_setup.plain_language_explanation import (
        explain_backend_vs_frontend,
        explain_what_node_does,
        explain_what_pnpm_does,
        explain_what_to_do_next,
        explain_why_3000_not_open,
    )
    from guided_setup.setup_requirement_detector import detect_setup_requirements, summarize_setup_requirements
    from guided_setup.setup_step_model import build_mac_setup_steps, build_setup_steps, build_windows_setup_steps, mark_setup_steps_status
    from runtime.security_scan import scan_guided_setup_outputs

    assert boundary()["guided_setup_only"] is True
    requirements = detect_setup_requirements()
    requirement_summary = summarize_setup_requirements(requirements)
    steps = build_setup_steps()
    mac_steps = build_mac_setup_steps()
    windows_steps = build_windows_setup_steps()
    marked = mark_setup_steps_status(requirements)
    commands = build_command_copy_blocks()
    wizard = build_guided_setup_wizard()
    summary = summarize_guided_setup_wizard(wizard)
    report = generate_guided_setup_report()
    safety = build_guided_setup_safety_summary()

    assert "likely_blocker" in requirements
    assert requirement_summary["likely_blocker"]
    assert len(steps) >= 12
    assert mac_steps and windows_steps
    for step in marked["steps"]:
        assert step["auto_run_allowed"] is False
        assert step["status"] in {"pending", "done", "blocked", "warning"}
        assert step["why_needed"]
    assert build_mac_command_blocks()
    assert build_windows_command_blocks()
    assert commands["command_blocks"]
    assert all(block["auto_run_allowed"] is False for block in commands["command_blocks"])
    assert "3000" in explain_why_3000_not_open(requirements)[0]
    assert "8000" in " ".join(explain_backend_vs_frontend())
    assert "Node.js" in " ".join(explain_what_node_does())
    assert "pnpm" in " ".join(explain_what_pnpm_does())
    assert explain_what_to_do_next(requirements)
    assert wizard["likely_blocker"]
    assert wizard["recommended_next_step"]
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert report["report_generated"] is True
    assert summarize_guided_setup_report(report)["report_generated"] is True
    assert safety["safe"] is True
    assert validate_guided_setup_safety({"target": "https://example.com"})["safe"] is False
    assert validate_guided_setup_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_guided_setup_safety({"payload": "raw provider payload"})["safe"] is False
    assert report["path"].endswith("reports/v5_43_guided_setup_wizard_report.md")
    assert scan_guided_setup_outputs(report)["safe"] is True
    for payload in [requirements, requirement_summary, marked, commands, wizard, summary, report, safety]:
        assert _safe_payload(payload)


def test_guided_setup_api_endpoints_return_locked_flags():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/guided-setup/status",
        "/api/v5/guided-setup/requirements",
        "/api/v5/guided-setup/steps",
        "/api/v5/guided-setup/commands",
        "/api/v5/guided-setup/explain",
        "/api/v5/guided-setup/safety",
        "/api/v5/guided-setup/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "guided_setup_only" in text
        assert "localhost_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _safe_payload(payload)


def test_cli_frontend_docs_navigation_and_security_scan_are_present():
    for args in [
        [],
        ["--check", "requirements"],
        ["--check", "steps"],
        ["--check", "commands"],
        ["--check", "explain"],
        ["--check", "safety"],
        ["--check", "report"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v543_guided_setup_wizard.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["guided_setup_only"] is True
        assert _safe_payload(payload)

    page = Path("web/frontend/app/v5-guided-setup/page.tsx").read_text(encoding="utf-8")
    api_client = Path("web/frontend/app/lib/apiClient.ts").read_text(encoding="utf-8")
    shell = Path("web/frontend/app/components/ProductionShell.tsx").read_text(encoding="utf-8")
    docs = Path("docs/V5_GUIDED_SETUP.md").read_text(encoding="utf-8")
    scanner = Path("runtime/security_scan.py").read_text(encoding="utf-8")
    assert "Guided Local Setup Wizard" in page
    assert "如果 127.0.0.1:3000 打不开，通常是前端没有启动" in page
    assert "Node.js 是运行网页前端需要的工具" in page
    assert "pnpm 是安装前端依赖需要的工具" in page
    assert "这个向导不会自动安装任何东西" in page
    assert "这个向导不会连接券商或提交订单" in page
    assert "fetchV5GuidedSetupSummary" in api_client
    assert "fetchV5GuidedSetupCommands" in api_client
    assert "V5 Guided Setup" in shell
    assert "V5.43 Guided Local Setup Wizard" in docs
    assert "scan_guided_setup_outputs" in scanner
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
        "auto_install_enabled\": true",
        "external_network_enabled\": true",
        "system_path_modify_enabled\": true",
        "admin_permission_required\": true",
        "long_running_process_start_enabled\": true",
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

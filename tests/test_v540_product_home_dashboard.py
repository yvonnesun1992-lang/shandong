from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


LOCKED_FALSE_KEYS = [
    "product_home_runtime_enabled",
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


def test_product_home_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_product_home_config import get_product_home_mode, get_product_home_status

    status = get_product_home_status()
    assert get_product_home_mode() == "product_home_only"
    assert status["product_home_mode"] == "product_home_only"
    assert status["product_home_only"] is True
    assert status["dashboard_read_only"] is True
    assert status["localhost_only"] is True
    assert status["paper_trading"] is True
    for key in LOCKED_FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_PRODUCT_HOME_MODE", "production")
    for env_name in [
        "SHANDONG_V5_ENABLE_PRODUCT_HOME_RUNTIME",
        "SHANDONG_V5_ENABLE_SANDBOX_API",
        "SHANDONG_V5_ENABLE_SECRET_READ",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION",
        "SHANDONG_V5_ENABLE_REAL_MONEY",
    ]:
        monkeypatch.setenv(env_name, "true")
    blocked = get_product_home_status()
    warnings = " | ".join(blocked["warnings"]).lower()
    assert get_product_home_mode() == "product_home_only"
    assert blocked["product_home_mode"] == "product_home_only"
    assert "mode override requested but blocked in v5.40" in warnings
    assert "sandbox api requested but blocked in v5.40" in warnings
    assert "secret read requested but blocked in v5.40" in warnings
    assert "account read requested but blocked in v5.40" in warnings
    assert "order submission requested but blocked in v5.40" in warnings
    assert "real money requested but blocked in v5.40" in warnings
    for key in LOCKED_FALSE_KEYS:
        assert blocked[key] is False
    assert _safe_payload(blocked)


def test_product_home_summaries_orchestrator_report_and_safety():
    from product_home.backtest_summary import build_backtest_summary
    from product_home.init import boundary
    from product_home.main_feature_cards import build_main_feature_cards
    from product_home.paper_trading_summary import build_paper_trading_summary
    from product_home.product_home_orchestrator import build_product_home_dashboard, summarize_product_home_dashboard
    from product_home.product_home_report import generate_product_home_report
    from product_home.product_home_safety_validator import build_product_home_safety_summary, validate_product_home_safety
    from product_home.recent_activity_summary import build_recent_activity_summary
    from product_home.risk_boundary_summary import build_risk_boundary_summary
    from product_home.runtime_visibility_summary import build_runtime_visibility_summary
    from product_home.system_health_summary import build_system_health_summary, summarize_system_health
    from runtime.security_scan import scan_product_home_outputs

    assert boundary()["product_home_only"] is True
    health = build_system_health_summary()
    runtime = build_runtime_visibility_summary()
    paper = build_paper_trading_summary()
    backtest = build_backtest_summary()
    risk = build_risk_boundary_summary()
    activity = build_recent_activity_summary(limit=5)
    cards = build_main_feature_cards()
    dashboard = build_product_home_dashboard()
    summary = summarize_product_home_dashboard(dashboard)
    safety = build_product_home_safety_summary()
    report = generate_product_home_report()

    assert health["system_health"] in {"OK", "WARNING", "FAIL"}
    assert summarize_system_health(health)["system_health"] == health["system_health"]
    assert runtime["runtime_visible"] is True
    assert paper["paper_trading_available"] is True
    assert paper["broker_connected"] is False
    assert paper["sandbox_api_enabled"] is False
    assert paper["order_submission_enabled"] is False
    assert backtest["backtest_module_available"] is True
    assert risk["safety_status"] == "OK"
    for key in LOCKED_FALSE_KEYS:
        assert risk[key] is False
    assert isinstance(activity["recent_items"], list)
    assert {card["title"] for card in cards} >= {"Quant Research", "Backtest", "Paper Trading", "Risk Monitor", "Local Launcher", "Safety Boundary"}
    assert dashboard["product_home_ready"] is True
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert safety["safe"] is True
    assert validate_product_home_safety({"product_home_only": False})["safe"] is False
    assert validate_product_home_safety({"sandbox_api_enabled": True})["safe"] is False
    assert validate_product_home_safety({"url": "https://example.com"})["safe"] is False
    assert report["path"].endswith("reports/v5_40_product_home_dashboard_report.md")
    assert scan_product_home_outputs(report)["safe"] is True
    for payload in [health, runtime, paper, backtest, risk, activity, cards, dashboard, summary, safety, report]:
        assert _safe_payload(payload)


def test_product_home_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/product-home/status",
        "/api/v5/product-home/system-health",
        "/api/v5/product-home/runtime",
        "/api/v5/product-home/paper-trading",
        "/api/v5/product-home/backtest",
        "/api/v5/product-home/risk-boundary",
        "/api/v5/product-home/recent-activity",
        "/api/v5/product-home/feature-cards",
        "/api/v5/product-home/safety",
        "/api/v5/product-home/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "product_home_only" in text
        assert "dashboard_read_only" in text
        assert "localhost_only" in text
        assert "paper_trading" in text
        for key in LOCKED_FALSE_KEYS:
            assert key in text
        assert _safe_payload(payload)


def test_cli_frontend_home_navigation_and_docs_are_present():
    for args in [
        [],
        ["--check", "health"],
        ["--check", "runtime"],
        ["--check", "paper"],
        ["--check", "backtest"],
        ["--check", "risk"],
        ["--check", "cards"],
        ["--check", "safety"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v540_product_home_dashboard.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["product_home_only"] is True
        assert _safe_payload(payload)

    page = Path("web/frontend/app/page.tsx").read_text(encoding="utf-8")
    api_client = Path("web/frontend/app/lib/apiClient.ts").read_text(encoding="utf-8")
    shell = Path("web/frontend/app/components/ProductionShell.tsx").read_text(encoding="utf-8")
    docs = Path("docs/V5_PRODUCT_HOME_DASHBOARD.md").read_text(encoding="utf-8")
    scanner = Path("runtime/security_scan.py").read_text(encoding="utf-8")
    assert "Shandong Quant System" in page
    assert "Local-first paper trading and research dashboard" in page
    assert "No real broker connected" in page
    assert "No real money" in page
    assert "No order submission" in page
    assert "fetchV5ProductHomeSummary" in api_client
    assert "fetchV5ProductHomeSystemHealth" in api_client
    assert "Home" in shell
    assert "V5 Product Home" in shell
    assert "V5.40 Product Home Dashboard" in docs
    assert "scan_product_home_outputs" in scanner
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

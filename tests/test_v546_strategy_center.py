from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


LOCKED_FALSE_KEYS = [
    "strategy_center_runtime_enabled",
    "advanced_code_view_enabled",
    "real_trading_enabled",
    "broker_connected",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "balance_read_enabled",
    "position_read_enabled",
    "order_preview_enabled",
    "order_submission_enabled",
    "real_money_enabled",
]


def test_strategy_center_config_blocks_env_requests(monkeypatch):
    from config.v5_strategy_center_config import get_strategy_center_mode, get_strategy_center_status

    status = get_strategy_center_status()
    assert get_strategy_center_mode() == "strategy_center_only"
    assert status["strategy_center_mode"] == "strategy_center_only"
    assert status["strategy_center_only"] is True
    assert status["localhost_only"] is True
    assert status["user_friendly_strategy_library"] is True
    assert status["code_editor_visible_by_default"] is False
    assert status["one_click_backtest_enabled"] is True
    assert status["paper_trading_preview_enabled"] is True
    assert status["paper_trading"] is True
    for key in LOCKED_FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_STRATEGY_CENTER_MODE", "production")
    for env_name in [
        "SHANDONG_V5_ENABLE_STRATEGY_CENTER_RUNTIME",
        "SHANDONG_V5_ENABLE_ADVANCED_CODE_VIEW",
        "SHANDONG_V5_ENABLE_REAL_TRADING",
        "SHANDONG_V5_ENABLE_SANDBOX_API",
        "SHANDONG_V5_ENABLE_SECRET_READ",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION",
        "SHANDONG_V5_ENABLE_REAL_MONEY",
    ]:
        monkeypatch.setenv(env_name, "true")
    blocked = get_strategy_center_status()
    warnings = " | ".join(blocked["warnings"]).lower()
    assert blocked["strategy_center_mode"] == "strategy_center_only"
    assert "mode override requested but blocked in v5.46" in warnings
    assert "real trading requested but blocked in v5.46" in warnings
    assert "sandbox api requested but blocked in v5.46" in warnings
    assert "secret read requested but blocked in v5.46" in warnings
    assert "account read requested but blocked in v5.46" in warnings
    assert "order submission requested but blocked in v5.46" in warnings
    assert "real money requested but blocked in v5.46" in warnings
    for key in LOCKED_FALSE_KEYS:
        assert blocked[key] is False
    assert _safe_payload(blocked)


def test_strategy_catalog_search_recommendations_cards_and_detail():
    from strategy_center.strategy_backtest_preview import build_backtest_preview
    from strategy_center.strategy_card_model import build_strategy_card, build_strategy_cards
    from strategy_center.strategy_catalog import (
        build_strategy_catalog,
        list_beginner_strategies,
        list_recommended_strategies,
        list_strategy_categories,
    )
    from strategy_center.strategy_detail_model import build_strategy_detail
    from strategy_center.strategy_education_copy import (
        explain_backtest,
        explain_paper_trading,
        explain_risk_level,
        explain_why_not_real_trading,
    )
    from strategy_center.strategy_paper_trading_preview import build_paper_trading_preview
    from strategy_center.strategy_recommendation import build_strategy_recommendation_panel
    from strategy_center.strategy_search import build_strategy_search_result, search_strategies

    catalog = build_strategy_catalog()
    categories = list_strategy_categories()
    recommended = list_recommended_strategies()
    beginner = list_beginner_strategies()
    search = search_strategies("小市值")
    filtered = build_strategy_search_result("红利", {"risk_level": "low"})
    panel = build_strategy_recommendation_panel()
    cards = build_strategy_cards(catalog)
    detail = build_strategy_detail("small_cap_momentum")
    backtest = build_backtest_preview("small_cap_momentum")
    paper = build_paper_trading_preview("small_cap_momentum")

    assert len(catalog) >= 10
    assert {"新手推荐", "稳健收益", "小市值策略", "红利低波策略", "指数增强策略"}.issubset(set(categories))
    assert len(recommended) >= 3
    assert len(beginner) >= 2
    assert any(item["strategy_id"] == "small_cap_momentum" for item in search)
    assert filtered["strategy_center_only"] is True
    assert filtered["total"] >= 1
    assert panel["next_action"] == "run_backtest"
    assert panel["real_trading_enabled"] is False
    assert cards and all("一键回测" in card["actions"] for card in cards)
    assert cards and all(card["real_trading_visible"] is False for card in cards)
    assert build_strategy_card(catalog[0])["code_visible_by_default"] is False
    assert detail["advanced_code_entry"]["collapsed_by_default"] is True
    assert detail["real_trading_enabled"] is False
    assert backtest["can_run_backtest"] is True
    assert backtest["real_trading_enabled"] is False
    assert paper["paper_trading_available"] is True
    assert paper["order_submission_enabled"] is False
    assert "普通" in explain_backtest()
    assert "模拟" in explain_paper_trading()
    assert "风险" in explain_risk_level("high")
    assert "真实交易" in explain_why_not_real_trading()
    for payload in [catalog, categories, recommended, beginner, search, filtered, panel, cards, detail, backtest, paper]:
        assert _safe_payload(payload)


def test_strategy_center_orchestrator_safety_report_and_cli():
    from strategy_center.strategy_center_orchestrator import build_strategy_center_dashboard, summarize_strategy_center
    from strategy_center.strategy_center_report import generate_strategy_center_report
    from strategy_center.strategy_center_safety_validator import (
        build_strategy_center_safety_summary,
        validate_strategy_center_safety,
    )

    dashboard = build_strategy_center_dashboard()
    summary = summarize_strategy_center(dashboard)
    safety = build_strategy_center_safety_summary()
    report = generate_strategy_center_report()

    assert dashboard["strategy_center_ready"] is True
    assert dashboard["strategy_center_only"] is True
    assert dashboard["verdict"] in {"PASS", "WARNING"}
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert safety["safe"] is True
    assert validate_strategy_center_safety({"broker_connected": True})["safe"] is False
    assert validate_strategy_center_safety({"order_submission_enabled": True})["safe"] is False
    assert report["path"].endswith("reports/v5_46_strategy_center_report.md")
    assert Path(report["path"]).exists()
    assert _safe_payload(dashboard)
    assert _safe_payload(safety)

    for args in [
        [],
        ["--check", "catalog"],
        ["--check", "search"],
        ["--check", "recommendations"],
        ["--check", "cards"],
        ["--check", "detail"],
        ["--check", "education"],
        ["--check", "safety"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v546_strategy_center.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["strategy_center_only"] is True
        assert _safe_payload(payload)


def test_strategy_center_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/strategy-center/status",
        "/api/v5/strategy-center/catalog",
        "/api/v5/strategy-center/categories",
        "/api/v5/strategy-center/recommendations",
        "/api/v5/strategy-center/search?query=小市值&risk_level=medium",
        "/api/v5/strategy-center/cards",
        "/api/v5/strategy-center/detail/small_cap_momentum",
        "/api/v5/strategy-center/backtest-preview/small_cap_momentum",
        "/api/v5/strategy-center/paper-preview/small_cap_momentum",
        "/api/v5/strategy-center/education",
        "/api/v5/strategy-center/safety",
        "/api/v5/strategy-center/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload, ensure_ascii=False, default=str).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "strategy_center_only" in text
        assert "localhost_only" in text
        assert "paper_trading" in text
        assert '"real_trading_enabled": false' in text
        assert '"broker_connected": false' in text
        assert '"sandbox_api_enabled": false' in text
        assert '"order_submission_enabled": false' in text
        assert '"real_money_enabled": false' in text
        assert _safe_payload(payload)


def test_strategy_center_frontend_and_api_client_are_present():
    strategy_page = Path("web/frontend/app/strategies/page.tsx")
    detail_page = Path("web/frontend/app/strategies/[strategyId]/page.tsx")
    api_client = Path("web/frontend/app/lib/apiClient.ts").read_text(encoding="utf-8")
    shell = Path("web/frontend/app/components/ProductionShell.tsx").read_text(encoding="utf-8")

    assert strategy_page.exists()
    assert detail_page.exists()
    page_text = strategy_page.read_text(encoding="utf-8")
    detail_text = detail_page.read_text(encoding="utf-8")
    for text in [
        "策略中心",
        "找到适合你的量化投资策略，不需要写代码。",
        "搜索策略：小市值、红利、动量、低估值、指数增强",
        "系统推荐",
        "新手推荐",
        "一键回测",
        "加入模拟交易",
        "当前仅支持回测和模拟交易",
    ]:
        assert text in page_text
    for text in ["适合谁", "不适合谁", "回测表现", "风险指标", "模拟交易预览", "高级代码"]:
        assert text in detail_text
    for fn_name in [
        "fetchV5StrategyCenterStatus",
        "fetchV5StrategyCenterCatalog",
        "fetchV5StrategyCenterCategories",
        "fetchV5StrategyCenterRecommendations",
        "fetchV5StrategyCenterSearch",
        "fetchV5StrategyCenterCards",
        "fetchV5StrategyCenterDetail",
        "fetchV5StrategyCenterBacktestPreview",
        "fetchV5StrategyCenterPaperPreview",
        "fetchV5StrategyCenterEducation",
        "fetchV5StrategyCenterSafety",
        "fetchV5StrategyCenterSummary",
    ]:
        assert fn_name in api_client
    assert "策略中心" in shell
    assert _safe_text(page_text + detail_text + api_client + shell)


def _safe_payload(payload: object) -> bool:
    return _safe_text(json.dumps(payload, ensure_ascii=False, default=str))


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
        '"broker_connected": true',
        '"sandbox_api_enabled": true',
        '"secret_read_enabled": true',
        '"account_read_enabled": true',
        '"balance_read_enabled": true',
        '"position_read_enabled": true',
        '"order_submission_enabled": true',
        '"real_money_enabled": true',
    ]
    return not any(term in lowered for term in blocked)

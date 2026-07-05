from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


LOCKED_FALSE_KEYS = [
    "backtest_dashboard_runtime_enabled",
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


def test_backtest_dashboard_config_blocks_env_requests(monkeypatch):
    from config.v5_backtest_dashboard_config import get_backtest_dashboard_mode, get_backtest_dashboard_status

    status = get_backtest_dashboard_status()
    assert get_backtest_dashboard_mode() == "backtest_dashboard_only"
    assert status["backtest_dashboard_mode"] == "backtest_dashboard_only"
    assert status["backtest_dashboard_only"] is True
    assert status["localhost_only"] is True
    assert status["user_friendly_backtest_report"] is True
    assert status["advanced_metrics_collapsed_by_default"] is True
    assert status["one_click_rebacktest_enabled"] is True
    assert status["paper_trading_entry_enabled"] is True
    assert status["paper_trading"] is True
    for key in LOCKED_FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_BACKTEST_DASHBOARD_MODE", "production")
    for env_name in [
        "SHANDONG_V5_ENABLE_BACKTEST_DASHBOARD_RUNTIME",
        "SHANDONG_V5_ENABLE_ADVANCED_METRICS_EXPANDED",
        "SHANDONG_V5_ENABLE_REAL_TRADING",
        "SHANDONG_V5_ENABLE_SANDBOX_API",
        "SHANDONG_V5_ENABLE_SECRET_READ",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION",
        "SHANDONG_V5_ENABLE_REAL_MONEY",
    ]:
        monkeypatch.setenv(env_name, "true")
    blocked = get_backtest_dashboard_status()
    warnings = " | ".join(blocked["warnings"]).lower()
    assert blocked["backtest_dashboard_mode"] == "backtest_dashboard_only"
    assert blocked["advanced_metrics_collapsed_by_default"] is True
    assert "mode override requested but blocked in v5.47" in warnings
    assert "real trading requested but blocked in v5.47" in warnings
    assert "sandbox api requested but blocked in v5.47" in warnings
    assert "secret read requested but blocked in v5.47" in warnings
    assert "account read requested but blocked in v5.47" in warnings
    assert "order submission requested but blocked in v5.47" in warnings
    assert "real money requested but blocked in v5.47" in warnings
    for key in LOCKED_FALSE_KEYS:
        assert blocked[key] is False
    assert _safe_payload(blocked)


def test_backtest_models_conclusion_risk_cards_charts_actions():
    from backtest_dashboard.backtest_action_panel import build_backtest_action_panel, build_next_steps
    from backtest_dashboard.backtest_chart_model import (
        build_daily_trade_action_chart_data,
        build_drawdown_chart_data,
        build_equity_curve_chart_data,
        build_excess_return_chart_data,
    )
    from backtest_dashboard.backtest_conclusion_engine import build_backtest_conclusion, build_user_friendly_verdict, evaluate_backtest_result
    from backtest_dashboard.backtest_result_model import (
        build_backtest_advanced_metrics,
        build_backtest_core_metrics,
        build_backtest_metadata,
        build_backtest_result,
    )
    from backtest_dashboard.backtest_risk_analysis import build_risk_analysis, build_risk_summary_for_user, classify_backtest_risk
    from backtest_dashboard.backtest_summary_cards import build_advanced_metric_cards, build_core_metric_cards
    from backtest_dashboard.metric_explanation_copy import build_metric_explanations, explain_max_drawdown, explain_strategy_return

    strategy_id = "small_cap_momentum"
    result = build_backtest_result(strategy_id)
    metadata = build_backtest_metadata(strategy_id)
    core = build_backtest_core_metrics(strategy_id)
    advanced = build_backtest_advanced_metrics(strategy_id)
    evaluation = evaluate_backtest_result(core)
    conclusion = build_backtest_conclusion(core)
    verdict = build_user_friendly_verdict(core)
    risk = build_risk_analysis(core)
    core_cards = build_core_metric_cards(core)
    advanced_cards = build_advanced_metric_cards(advanced)
    equity = build_equity_curve_chart_data(strategy_id)
    daily_excess = build_excess_return_chart_data(strategy_id)
    trades = build_daily_trade_action_chart_data(strategy_id)
    drawdown = build_drawdown_chart_data(strategy_id)
    actions = build_backtest_action_panel(strategy_id, conclusion)

    assert result["backtest_dashboard_only"] is True
    assert metadata["strategy_id"] == strategy_id
    assert metadata["display_name"]
    assert metadata["initial_capital"] > 0
    assert metadata["benchmark"]
    assert metadata["trading_mode"] == "paper_trading"
    assert metadata["real_trading_enabled"] is False
    assert core["strategy_return"] != 0
    assert {"strategy_return", "benchmark_return", "excess_return", "max_drawdown", "win_rate"}.issubset(core)
    assert {"alpha", "beta", "information_ratio", "sortino", "volatility"}.issubset(advanced)
    assert evaluation["real_trading_enabled"] is False
    assert "策略" in conclusion["user_summary"]
    assert verdict["user_friendly"] is True
    assert classify_backtest_risk({"max_drawdown": 0.04}) == "low"
    assert classify_backtest_risk({"max_drawdown": 0.10}) == "medium"
    assert classify_backtest_risk({"max_drawdown": 0.20}) == "high"
    assert risk["paper_trading_allowed"] is True
    assert risk["real_trading_enabled"] is False
    assert "风险" in build_risk_summary_for_user(core)["risk_reason"]
    assert [card["label"] for card in core_cards][:3] == ["策略收益", "基准收益", "超额收益"]
    assert any(card["label"] == "最大回撤" for card in core_cards)
    assert any(card["label"] == "胜率" for card in core_cards)
    assert any(card["label"] == "Alpha" for card in advanced_cards)
    assert any(card["label"] == "Beta" for card in advanced_cards)
    assert any(card["label"] == "信息比率" for card in advanced_cards)
    assert all(card["collapsed_by_default"] is True for card in advanced_cards)
    assert len(equity["points"]) >= 5
    assert {"date", "strategy_return", "benchmark_return", "excess_return"}.issubset(equity["points"][0])
    assert daily_excess["points"][0]["direction"] in {"outperform", "underperform"}
    assert {"buy_amount", "sell_amount", "net_amount"}.issubset(trades["points"][0])
    assert drawdown["points"][0]["drawdown"] <= 0
    assert any(action["action_id"] == "rebacktest" and action["enabled"] for action in actions["actions"])
    assert any(action["action_id"] == "paper_trade" for action in actions["actions"])
    assert all(action.get("real_trading_enabled") is False for action in actions["actions"])
    assert all(action["action_id"] != "real_trade" for action in actions["actions"])
    assert "策略在回测期间赚了多少" in explain_strategy_return()
    assert "最差的时候亏了多少" in explain_max_drawdown()
    assert "Alpha" in build_metric_explanations()
    assert _safe_payload(result)


def test_backtest_dashboard_orchestrator_safety_report_and_cli():
    from backtest_dashboard.backtest_dashboard_orchestrator import build_backtest_dashboard, summarize_backtest_dashboard
    from backtest_dashboard.backtest_dashboard_report import generate_backtest_dashboard_report
    from backtest_dashboard.backtest_dashboard_safety_validator import (
        build_backtest_dashboard_safety_summary,
        validate_backtest_dashboard_safety,
    )

    dashboard = build_backtest_dashboard("small_cap_momentum")
    summary = summarize_backtest_dashboard(dashboard)
    safety = build_backtest_dashboard_safety_summary()
    report = generate_backtest_dashboard_report("small_cap_momentum")

    assert dashboard["backtest_dashboard_ready"] is True
    assert dashboard["backtest_dashboard_only"] is True
    assert dashboard["verdict"] in {"PASS", "WARNING"}
    assert summary["verdict"] in {"PASS", "WARNING"}
    assert safety["safe"] is True
    assert validate_backtest_dashboard_safety({"broker_connected": True})["safe"] is False
    assert validate_backtest_dashboard_safety({"order_submission_enabled": True})["safe"] is False
    assert report["path"].endswith("reports/v5_47_backtest_dashboard_report.md")
    assert Path(report["path"]).exists()
    assert _safe_payload(dashboard)
    assert _safe_payload(safety)

    for args in [
        [],
        ["--strategy", "small_cap_momentum"],
        ["--check", "result"],
        ["--check", "conclusion"],
        ["--check", "metrics"],
        ["--check", "charts"],
        ["--check", "risk"],
        ["--check", "actions"],
        ["--check", "safety"],
    ]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v547_backtest_dashboard.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["backtest_dashboard_only"] is True
        assert _safe_payload(payload)


def test_backtest_dashboard_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/backtest-dashboard/status",
        "/api/v5/backtest-dashboard/result/small_cap_momentum",
        "/api/v5/backtest-dashboard/conclusion/small_cap_momentum",
        "/api/v5/backtest-dashboard/metrics/small_cap_momentum",
        "/api/v5/backtest-dashboard/risk/small_cap_momentum",
        "/api/v5/backtest-dashboard/charts/small_cap_momentum",
        "/api/v5/backtest-dashboard/actions/small_cap_momentum",
        "/api/v5/backtest-dashboard/explanations",
        "/api/v5/backtest-dashboard/safety",
        "/api/v5/backtest-dashboard/summary/small_cap_momentum",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload, ensure_ascii=False, default=str).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "backtest_dashboard_only" in text
        assert "localhost_only" in text
        assert "paper_trading" in text
        assert '"real_trading_enabled": false' in text
        assert '"broker_connected": false' in text
        assert '"sandbox_api_enabled": false' in text
        assert '"order_submission_enabled": false' in text
        assert '"real_money_enabled": false' in text
        assert _safe_payload(payload)


def test_backtest_dashboard_frontend_routes_and_api_client_are_present():
    backtest_page = Path("web/frontend/app/backtest/[strategyId]/page.tsx")
    strategies_page = Path("web/frontend/app/strategies/page.tsx")
    home_page = Path("web/frontend/app/page.tsx")
    api_client = Path("web/frontend/app/lib/apiClient.ts").read_text(encoding="utf-8")
    shell = Path("web/frontend/app/components/ProductionShell.tsx").read_text(encoding="utf-8")

    assert backtest_page.exists()
    page_text = backtest_page.read_text(encoding="utf-8")
    for text in [
        "回测结果",
        "用普通投资者能看懂的方式，判断这个策略是否值得继续观察。",
        "策略信息栏",
        "系统结论",
        "核心指标",
        "收益曲线",
        "每日跑赢 / 跑输图",
        "每日交易动作图",
        "风险分析",
        "交易记录",
        "高级指标",
        "当前仅为回测和模拟交易环境，不连接真实券商，不使用真实资金，不提交真实订单。",
    ]:
        assert text in page_text
    for fn_name in [
        "fetchV5BacktestDashboardStatus",
        "fetchV5BacktestDashboardResult",
        "fetchV5BacktestDashboardConclusion",
        "fetchV5BacktestDashboardMetrics",
        "fetchV5BacktestDashboardRisk",
        "fetchV5BacktestDashboardCharts",
        "fetchV5BacktestDashboardActions",
        "fetchV5BacktestDashboardExplanations",
        "fetchV5BacktestDashboardSafety",
        "fetchV5BacktestDashboardSummary",
    ]:
        assert fn_name in api_client
    assert "回测" in shell
    assert "策略中心" in shell
    assert "/backtest/small_cap_momentum" in strategies_page.read_text(encoding="utf-8")
    assert "/backtest/small_cap_momentum" in home_page.read_text(encoding="utf-8")
    assert _safe_text(page_text + api_client + shell)


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

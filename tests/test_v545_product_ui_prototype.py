from __future__ import annotations

import json
from pathlib import Path


def test_product_ui_config_and_one_click_summary_are_locked():
    from product_ui.init import get_product_ui_status
    from product_ui.one_click_investment import (
        run_backtest,
        run_paper_trading,
        select_recommended_strategy,
        summarize_result,
    )
    from product_ui.ui_design_system import get_product_ui_design_system

    status = get_product_ui_status()
    assert status["product_ui_mode"] == "product_ui_only"
    assert status["localhost_only"] is True
    assert status["ui_mode_locked"] is True
    assert status["broker_connected"] is False
    assert status["sandbox_api_enabled"] is False
    assert status["order_submission_enabled"] is False
    assert status["real_money_enabled"] is False

    design = get_product_ui_design_system()
    assert design["theme"] == "institutional_quant_product"
    assert design["colors"]["primary"] == "#061525"
    assert design["colors"]["accent"] == "#C8A24A"
    assert design["typography"]["chinese"] == "PingFang SC"

    strategy = select_recommended_strategy()
    backtest = run_backtest(strategy)
    paper = run_paper_trading(strategy)
    summary = summarize_result(strategy, backtest, paper)

    assert strategy["strategy_name"] == "小市值动量策略"
    assert strategy["risk_level"] == "中"
    assert backtest["strategy_return"] > backtest["benchmark_return"]
    assert paper["paper_trading"] is True
    assert summary["recommended_to_continue"] is True
    assert summary["mode"] == "paper_trading_only"
    assert _safe_payload(summary)


def test_home_page_is_user_friendly_product_prototype():
    page = Path("web/frontend/app/page.tsx").read_text(encoding="utf-8")

    required_user_copy = [
        "Shandong Quantitative System",
        "Institutional Quant Investing Platform",
        "Paper Trading Mode",
        "Risk Control Enabled",
        "Local System Running",
        "今日收益",
        "本周收益",
        "月度收益",
        "最大回撤",
        "当前仓位",
        "市场状态",
        "一键开始投资",
        "查看策略表现",
        "运行回测",
        "推荐策略",
        "小市值动量策略",
        "震荡偏多",
        "可直接运行",
        "策略收益线",
        "基准收益线",
        "模拟交易环境",
        "无真实资金",
        "无真实交易",
    ]
    for text in required_user_copy:
        assert text in page

    engineering_terms = ["API", "CLI", "launcher", "doctor", "logs", "evidence", "debug"]
    for term in engineering_terms:
        assert term not in page.lower()
    assert _safe_text(page)


def test_product_navigation_hides_engineering_items_under_advanced_settings():
    shell = Path("web/frontend/app/components/ProductionShell.tsx").read_text(encoding="utf-8")
    visible_links = [
        "首页",
        "策略",
        "回测",
        "模拟交易",
        "风险",
        "数据",
        "帮助",
    ]
    for label in visible_links:
        assert label in shell

    assert "Advanced Settings" in shell
    for engineering_label in ["API", "CLI", "Launcher", "Doctor", "Logs", "Evidence", "Debug"]:
        assert engineering_label in shell
    assert _safe_text(shell)


def test_v545_review_docs_and_safety_boundaries_exist():
    review = Path("REVIEW_PACKAGE.md").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "V5.45 Product UI Prototype" in review
    assert "V5.45 Product UI Prototype" in readme
    assert "No broker connection" in review
    assert "No sandbox API" in review
    assert "No real money" in review

    combined = "\n".join(
        Path(path).read_text(encoding="utf-8", errors="ignore")
        for path in [
            "product_ui/init.py",
            "product_ui/one_click_investment.py",
            "product_ui/ui_design_system.py",
            "web/frontend/app/page.tsx",
            "web/frontend/app/components/ProductionShell.tsx",
        ]
    )
    assert "place_order(" not in combined
    assert "submit_real_order" not in combined
    assert "alpaca_trade_api" not in combined
    assert "ib_insync" not in combined
    assert "sk-" not in combined
    assert "eval(" not in combined
    assert "exec(" not in combined


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
        "broker_connected\": true",
        "sandbox_api_enabled\": true",
        "order_submission_enabled\": true",
        "real_money_enabled\": true",
    ]
    return not any(term in lowered for term in blocked)

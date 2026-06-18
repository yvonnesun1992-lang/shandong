from __future__ import annotations

import inspect

from src.reports.strategy_research_report import (
    RESEARCH_DISCLAIMER,
    build_strategy_research_report,
    strategy_report_to_markdown,
)


def backtest_summary() -> dict:
    return {
        "total_return": 0.18,
        "annualized_return": 0.22,
        "max_drawdown": -0.12,
        "number_of_trades": 18,
        "final_portfolio_value": 118000,
        "status": "success",
    }


def quality_summary(level: str = "Good") -> dict:
    return {
        "total_quality_score": 72,
        "quality_level": level,
        "return_score": 80,
        "drawdown_score": 70,
        "stability_score": 65,
        "out_of_sample_score": 60,
        "stress_score": 55,
        "data_quality_score": 80,
    }


def stability_summary() -> dict:
    return {"stability_level": "Medium", "success_windows": 5, "failed_windows": 1}


def out_of_sample_summary(level: str = "Medium") -> dict:
    return {"overfit_risk_level": level, "test_total_return": 0.08, "return_decay": 0.4}


def stress_summary(level: str = "Medium") -> dict:
    return {"overall_stress_level": level, "worst_stressed_return": -0.08, "worst_stressed_drawdown": -0.22}


def risk_summary() -> dict:
    return {"risk_level": "Low", "largest_position_pct": 0.15, "top3_position_pct": 0.45}


def test_normal_inputs_generate_report():
    report = build_strategy_research_report(
        "trend_default",
        ["AAPL", "MSFT"],
        backtest_summary(),
        quality_summary(),
        stability_summary=stability_summary(),
        out_of_sample_summary=out_of_sample_summary(),
        stress_summary=stress_summary(),
        risk_summary=risk_summary(),
    )

    assert report["report_title"] == "Strategy Research Report - trend_default"
    assert report["strategy_name"] == "trend_default"
    assert report["symbols"] == ["AAPL", "MSFT"]
    assert report["research_view"] in {"Positive", "Neutral", "Cautious"}
    assert report["key_metrics"]["quality_score"] == 72
    assert report["disclaimer"] == RESEARCH_DISCLAIMER


def test_missing_optional_modules_do_not_crash():
    report = build_strategy_research_report(
        "trend_default",
        ["AAPL"],
        backtest_summary(),
        quality_summary(),
    )

    assert report["module_summaries"]["stability"] == {}
    assert report["module_summaries"]["out_of_sample"] == {}
    assert report["module_summaries"]["stress"] == {}
    assert report["module_summaries"]["risk"] == {}
    assert any("缺少稳定性" in warning for warning in report["warnings"])


def test_good_quality_without_high_risk_is_positive_or_neutral():
    report = build_strategy_research_report(
        "trend_default",
        ["AAPL"],
        backtest_summary(),
        quality_summary("Good"),
        out_of_sample_summary=out_of_sample_summary("Low"),
        stress_summary=stress_summary("Low"),
    )

    assert report["research_view"] in {"Positive", "Neutral"}


def test_weak_quality_is_cautious():
    report = build_strategy_research_report("trend_default", ["AAPL"], backtest_summary(), quality_summary("Weak"))

    assert report["research_view"] == "Cautious"


def test_high_overfit_risk_is_cautious():
    report = build_strategy_research_report(
        "trend_default",
        ["AAPL"],
        backtest_summary(),
        quality_summary("Good"),
        out_of_sample_summary=out_of_sample_summary("High"),
    )

    assert report["research_view"] == "Cautious"


def test_high_stress_level_is_cautious():
    report = build_strategy_research_report(
        "trend_default",
        ["AAPL"],
        backtest_summary(),
        quality_summary("Good"),
        stress_summary=stress_summary("High"),
    )

    assert report["research_view"] == "Cautious"


def test_strategy_report_to_markdown_contains_required_sections():
    report = build_strategy_research_report(
        "trend_default",
        ["AAPL", "MSFT"],
        backtest_summary(),
        quality_summary(),
    )

    markdown = strategy_report_to_markdown(report)

    assert isinstance(markdown, str)
    assert "# Strategy Research Report - trend_default" in markdown
    assert "策略名称：trend_default" in markdown
    assert "股票池：AAPL, MSFT" in markdown
    assert "## 核心指标" in markdown
    assert RESEARCH_DISCLAIMER in markdown


def test_report_does_not_generate_real_trade_advice():
    report = build_strategy_research_report(
        "trend_default",
        ["AAPL"],
        backtest_summary(),
        quality_summary(),
    )
    markdown = strategy_report_to_markdown(report)
    forbidden = ["建议买入", "建议卖出", "保证收益", "真实交易指令"]

    combined = str(report) + markdown
    for phrase in forbidden:
        assert phrase not in combined


def test_strategy_research_report_module_keeps_research_only_boundaries():
    import src.reports.strategy_research_report as strategy_research_report

    source = inspect.getsource(strategy_research_report)
    forbidden = [
        "IB" + "KR",
        "富" + "途",
        "Al" + "paca",
        "Robin" + "hood",
        "broker " + "order",
        "place_" + "order",
        "real " + "trade",
        "api_" + "key",
        "sec" + "ret",
        "pass" + "word",
        "tok" + "en",
        "Open" + "AI API",
        "AI " + "prediction",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in source

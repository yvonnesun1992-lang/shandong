from __future__ import annotations

import inspect

from src.strategies.quality_score import (
    RESEARCH_DISCLAIMER,
    build_backtest_quality_score,
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


def stability_summary() -> dict:
    return {
        "stability_level": "Medium",
        "success_windows": 5,
        "failed_windows": 1,
        "return_consistency_score": 0.72,
        "drawdown_consistency_score": 0.68,
    }


def out_of_sample_summary() -> dict:
    return {
        "overfit_risk_level": "Medium",
        "train_total_return": 0.30,
        "test_total_return": 0.08,
        "return_decay": 0.73,
        "test_trades": 6,
    }


def stress_summary() -> dict:
    return {
        "overall_stress_level": "Medium",
        "worst_stressed_return": -0.08,
        "worst_stressed_drawdown": -0.22,
        "worst_estimated_loss": 8000,
    }


def test_normal_backtest_summary_generates_quality_score():
    report = build_backtest_quality_score(backtest_summary())

    summary = report["summary"]
    assert 0 <= summary["total_quality_score"] <= 100
    assert summary["quality_level"] in {"Excellent", "Good", "Watch", "Weak"}
    assert summary["return_score"] > 0
    assert summary["drawdown_score"] > 0
    assert summary["disclaimer"] == RESEARCH_DISCLAIMER
    assert report["score_breakdown"]
    assert report["checks"]


def test_complete_inputs_generate_composite_score():
    report = build_backtest_quality_score(
        backtest_summary(),
        stability_summary=stability_summary(),
        out_of_sample_summary=out_of_sample_summary(),
        stress_summary=stress_summary(),
    )

    summary = report["summary"]
    assert summary["stability_score"] > 0
    assert summary["out_of_sample_score"] > 0
    assert summary["stress_score"] > 0
    assert summary["data_quality_score"] > 0


def test_missing_optional_inputs_do_not_crash_and_warn():
    report = build_backtest_quality_score(backtest_summary())

    assert report["summary"]["data_quality_score"] < 100
    assert any("缺少稳定性" in warning for warning in report["warnings"])
    assert any("缺少样本外" in warning for warning in report["warnings"])
    assert any("缺少压力测试" in warning for warning in report["warnings"])


def test_negative_total_return_lowers_return_score():
    good = build_backtest_quality_score(backtest_summary())
    weak = build_backtest_quality_score({**backtest_summary(), "total_return": -0.08, "annualized_return": -0.1})

    assert weak["summary"]["return_score"] < good["summary"]["return_score"]


def test_large_drawdown_lowers_drawdown_score():
    normal = build_backtest_quality_score(backtest_summary())
    large = build_backtest_quality_score({**backtest_summary(), "max_drawdown": -0.40})

    assert large["summary"]["drawdown_score"] < normal["summary"]["drawdown_score"]


def test_high_overfit_risk_lowers_out_of_sample_score():
    medium = build_backtest_quality_score(backtest_summary(), out_of_sample_summary=out_of_sample_summary())
    high = build_backtest_quality_score(
        backtest_summary(),
        out_of_sample_summary={**out_of_sample_summary(), "overfit_risk_level": "High"},
    )

    assert high["summary"]["out_of_sample_score"] < medium["summary"]["out_of_sample_score"]


def test_high_stress_level_lowers_stress_score():
    medium = build_backtest_quality_score(backtest_summary(), stress_summary=stress_summary())
    high = build_backtest_quality_score(
        backtest_summary(),
        stress_summary={**stress_summary(), "overall_stress_level": "High"},
    )

    assert high["summary"]["stress_score"] < medium["summary"]["stress_score"]


def test_returns_total_quality_score_and_quality_level():
    report = build_backtest_quality_score(backtest_summary())

    assert "total_quality_score" in report["summary"]
    assert "quality_level" in report["summary"]


def test_score_breakdown_returns_required_fields():
    report = build_backtest_quality_score(backtest_summary())

    required = {"category", "score", "message"}
    for item in report["score_breakdown"]:
        assert required.issubset(item)


def test_quality_score_module_keeps_research_only_boundaries():
    import src.strategies.quality_score as quality_score

    source = inspect.getsource(quality_score)
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

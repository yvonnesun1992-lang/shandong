from __future__ import annotations

import inspect

import pandas as pd

from src.strategies.stability import (
    RESEARCH_DISCLAIMER,
    build_strategy_stability_report,
    split_backtest_windows,
)


def sample_backtest_results() -> list[dict]:
    return [
        {
            "window_name": "Window 1",
            "total_return": 0.12,
            "annualized_return": 0.24,
            "max_drawdown": -0.08,
            "number_of_trades": 8,
            "final_portfolio_value": 112000,
            "status": "success",
        },
        {
            "window_name": "Window 2",
            "total_return": 0.08,
            "annualized_return": 0.16,
            "max_drawdown": -0.10,
            "number_of_trades": 6,
            "final_portfolio_value": 108000,
            "status": "success",
        },
        {
            "window_name": "Window 3",
            "total_return": 0.05,
            "annualized_return": 0.10,
            "max_drawdown": -0.09,
            "number_of_trades": 5,
            "final_portfolio_value": 105000,
            "status": "success",
        },
    ]


def test_multiple_normal_windows_generate_stability_report():
    report = build_strategy_stability_report(sample_backtest_results())

    summary = report["summary"]
    assert summary["window_count"] == 3
    assert summary["success_windows"] == 3
    assert summary["failed_windows"] == 0
    assert summary["positive_return_windows"] == 3
    assert summary["stability_level"] in {"Low", "Medium", "High"}
    assert summary["disclaimer"] == RESEARCH_DISCLAIMER
    assert report["window_results"]
    assert report["checks"]


def test_partial_failed_windows_do_not_crash():
    results = sample_backtest_results() + [
        {"window_name": "Failed", "status": "failed", "error": "No symbols have enough data."}
    ]

    report = build_strategy_stability_report(results)

    assert report["summary"]["failed_windows"] == 1
    assert report["failed_windows"][0]["window_name"] == "Failed"
    assert any(check["name"] == "数据质量风险" and check["status"] == "warn" for check in report["checks"])
    assert any("部分窗口回测失败" in warning for warning in report["warnings"])


def test_success_windows_below_minimum_sets_low_or_warns():
    report = build_strategy_stability_report(sample_backtest_results()[:2], min_windows=3)

    assert report["summary"]["stability_level"] == "Low"
    assert any(check["name"] == "样本数量风险" and check["status"] == "fail" for check in report["checks"])
    assert any("样本数量不足" in warning for warning in report["warnings"])


def test_high_positive_return_ratio_passes_return_stability():
    report = build_strategy_stability_report(sample_backtest_results(), min_windows=3)

    assert any(check["name"] == "收益稳定性" and check["status"] == "pass" for check in report["checks"])


def test_bad_worst_drawdown_creates_warning_or_fail():
    results = sample_backtest_results()
    results[1] = {**results[1], "max_drawdown": -0.35}

    report = build_strategy_stability_report(results)

    assert report["summary"]["worst_max_drawdown"] == -0.35
    assert any(check["name"] == "回撤稳定性" and check["status"] == "fail" for check in report["checks"])
    assert any("回撤风险较高" in warning for warning in report["warnings"])


def test_large_return_variation_warns_about_instability():
    results = [
        {**sample_backtest_results()[0], "total_return": 0.45},
        {**sample_backtest_results()[1], "total_return": -0.20},
        {**sample_backtest_results()[2], "total_return": 0.04},
    ]

    report = build_strategy_stability_report(results)

    assert any(check["name"] == "收益稳定性" and check["status"] == "warn" for check in report["checks"])
    assert any("收益稳定性不足" in warning for warning in report["warnings"])


def test_empty_backtest_results_do_not_crash():
    report = build_strategy_stability_report([])

    assert report["summary"]["window_count"] == 0
    assert report["summary"]["success_windows"] == 0
    assert report["summary"]["stability_level"] == "Low"
    assert any("没有可用于稳定性评估" in warning for warning in report["warnings"])


def test_split_backtest_windows_with_dataframe():
    data = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "close": range(10),
        }
    )

    windows = split_backtest_windows(data, window_size=4, step_size=3)

    assert len(windows) == 3
    assert windows[0]["start_date"] == "2024-01-01"
    assert windows[0]["end_date"] == "2024-01-04"
    assert len(windows[0]["data"]) == 4


def test_split_backtest_windows_with_portfolio_data_dict():
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=8, freq="D"),
            "close": range(8),
        }
    )

    windows = split_backtest_windows({"AAPL": frame, "MSFT": frame}, window_size=4, step_size=4)

    assert len(windows) == 2
    assert sorted(windows[0]["data"]) == ["AAPL", "MSFT"]


def test_strategy_stability_module_keeps_research_only_boundaries():
    import src.strategies.stability as stability

    source = inspect.getsource(stability)
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

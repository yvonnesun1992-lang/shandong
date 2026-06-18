from __future__ import annotations

import inspect

import pandas as pd

from src.strategies.out_of_sample import (
    RESEARCH_DISCLAIMER,
    build_out_of_sample_report,
    split_train_test_data,
)


def train_result() -> dict:
    return {
        "period_name": "Train",
        "total_return": 0.30,
        "annualized_return": 0.25,
        "max_drawdown": -0.12,
        "number_of_trades": 20,
        "final_portfolio_value": 130000,
        "status": "success",
    }


def sample_test_result() -> dict:
    return {
        "period_name": "Out-of-sample",
        "total_return": 0.18,
        "annualized_return": 0.16,
        "max_drawdown": -0.14,
        "number_of_trades": 6,
        "final_portfolio_value": 118000,
        "status": "success",
    }


def test_normal_train_and_test_generate_report():
    report = build_out_of_sample_report(train_result(), sample_test_result())

    summary = report["summary"]
    assert summary["train_total_return"] == 0.30
    assert summary["test_total_return"] == 0.18
    assert summary["train_trades"] == 20
    assert summary["test_trades"] == 6
    assert summary["test_trade_sample_ok"] is True
    assert summary["overfit_risk_level"] in {"Low", "Medium", "High"}
    assert summary["disclaimer"] == RESEARCH_DISCLAIMER
    assert len(report["period_results"]) == 2
    assert report["checks"]


def test_positive_train_negative_test_is_high_risk():
    report = build_out_of_sample_report(train_result(), {**sample_test_result(), "total_return": -0.05})

    assert report["summary"]["overfit_risk_level"] == "High"
    assert any("样本外测试为负收益" in warning for warning in report["warnings"])


def test_failed_test_is_high_risk_without_crashing():
    failed_test = {**sample_test_result(), "status": "failed", "error": "No symbols have enough data."}

    report = build_out_of_sample_report(train_result(), failed_test)

    assert report["summary"]["overfit_risk_level"] == "High"
    assert any(check["name"] == "样本外测试表现" and check["status"] == "fail" for check in report["checks"])
    assert any("样本外测试区间回测失败" in warning for warning in report["warnings"])


def test_large_return_decay_warns_about_overfit_risk():
    weak_test = {**sample_test_result(), "total_return": 0.05}

    report = build_out_of_sample_report(train_result(), weak_test)

    assert report["summary"]["return_decay"] > 0.5
    assert any(check["name"] == "收益衰减" and check["status"] in {"warn", "fail"} for check in report["checks"])
    assert any("收益相对训练区间明显衰减" in warning for warning in report["warnings"])


def test_low_test_trades_warns_about_sample_size():
    report = build_out_of_sample_report(train_result(), {**sample_test_result(), "number_of_trades": 1}, min_test_trades=3)

    assert report["summary"]["test_trade_sample_ok"] is False
    assert any(check["name"] == "数据质量风险" and check["status"] == "warn" for check in report["checks"])
    assert any("样本数量不足" in warning for warning in report["warnings"])


def test_worse_test_drawdown_warns():
    report = build_out_of_sample_report(train_result(), {**sample_test_result(), "max_drawdown": -0.25})

    assert report["summary"]["drawdown_worsening"] > 0.08
    assert any(check["name"] == "回撤恶化" and check["status"] in {"warn", "fail"} for check in report["checks"])
    assert any("回撤" in warning and "更差" in warning for warning in report["warnings"])


def test_split_train_test_data_supports_dataframe():
    data = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=10), "close": range(10)})

    split = split_train_test_data(data, train_ratio=0.7)

    assert len(split["train"]) == 7
    assert len(split["test"]) == 3
    assert split["train_rows"] == 7
    assert split["test_rows"] == 3
    assert split["warnings"] == []
    assert len(data) == 10


def test_split_train_test_data_supports_price_data_dict():
    frame = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=10), "close": range(10)})

    split = split_train_test_data({"AAPL": frame, "MSFT": frame}, train_ratio=0.6)

    assert sorted(split["train"]) == ["AAPL", "MSFT"]
    assert len(split["train"]["AAPL"]) == 6
    assert len(split["test"]["AAPL"]) == 4
    assert split["train_rows"] == 6
    assert split["test_rows"] == 4


def test_split_train_test_data_handles_insufficient_data():
    split = split_train_test_data(pd.DataFrame({"close": [1]}))

    assert split["train_rows"] == 0
    assert split["test_rows"] == 0
    assert split["warnings"]


def test_train_ratio_is_clamped():
    data = pd.DataFrame({"close": range(10)})

    split = split_train_test_data(data, train_ratio=0.95)

    assert len(split["train"]) == 9
    assert len(split["test"]) == 1
    assert any("train_ratio" in warning for warning in split["warnings"])


def test_out_of_sample_module_keeps_research_only_boundaries():
    import src.strategies.out_of_sample as out_of_sample

    source = inspect.getsource(out_of_sample)
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

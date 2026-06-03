from __future__ import annotations

import pandas as pd
import pytest

from src.data.data_quality import build_data_quality_report, check_data_freshness, validate_ohlcv_data
from src.data.sample_data import load_sample_ohlcv


def test_validate_ohlcv_data_accepts_sample_data():
    data = load_sample_ohlcv("us", "NVDA")

    report = validate_ohlcv_data(data)

    assert report["is_valid"] is True
    assert report["errors"] == []
    assert report["row_count"] >= 120
    assert report["latest_close"] > 0


def test_validate_ohlcv_data_missing_columns_returns_error():
    data = load_sample_ohlcv("us", "NVDA").drop(columns=["close"])

    report = validate_ohlcv_data(data)

    assert report["is_valid"] is False
    assert "Missing columns" in report["errors"][0]


def test_validate_ohlcv_data_negative_price_returns_error():
    data = load_sample_ohlcv("us", "NVDA")
    data.loc[0, "close"] = -1

    report = validate_ohlcv_data(data)

    assert report["is_valid"] is False
    assert any("positive" in error for error in report["errors"])


def test_validate_ohlcv_data_high_low_errors():
    data = load_sample_ohlcv("us", "NVDA")
    data.loc[0, "high"] = 1
    data.loc[1, "low"] = 9999

    report = validate_ohlcv_data(data)

    assert report["is_valid"] is False
    assert any("High" in error for error in report["errors"])
    assert any("Low" in error for error in report["errors"])


def test_validate_ohlcv_data_date_not_increasing_returns_error():
    data = load_sample_ohlcv("us", "NVDA")
    data = data.sort_values("date", ascending=False).reset_index(drop=True)

    report = validate_ohlcv_data(data)

    assert report["is_valid"] is False
    assert any("Date column is not increasing" in error for error in report["errors"])


def test_check_data_freshness_detects_old_data():
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
            "open": [1, 1],
            "high": [2, 2],
            "low": [1, 1],
            "close": [1.5, 1.6],
            "volume": [100, 200],
        }
    )

    freshness = check_data_freshness(data, max_age_days=7)

    assert freshness["is_fresh"] is False
    assert freshness["age_days"] > 7
    assert freshness["warning"]


def test_check_data_freshness_rejects_missing_date():
    with pytest.raises(ValueError, match="date"):
        check_data_freshness(pd.DataFrame({"close": [1.0]}))


def test_build_data_quality_report_contains_expected_fields():
    report = build_data_quality_report("us", "NVDA", load_sample_ohlcv("us", "NVDA"))

    assert {"is_valid", "warnings", "errors", "row_count", "start_date", "end_date", "latest_close"}.issubset(report)
    assert report["market"] == "us"
    assert report["symbol"] == "NVDA"

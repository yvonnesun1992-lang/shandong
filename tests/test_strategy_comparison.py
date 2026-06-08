from __future__ import annotations

import inspect

import pandas as pd
import pytest

from src.data.sample_data import load_sample_ohlcv
from src.strategies.comparison import compare_strategy_presets
from src.strategies.presets import DEFAULT_STRATEGY_PRESETS


def sample_price_data() -> dict[str, pd.DataFrame]:
    return {
        "NVDA": load_sample_ohlcv("us", "NVDA"),
        "300308": load_sample_ohlcv("cn", "300308"),
    }


def test_compare_strategy_presets_runs_with_sample_data():
    result = compare_strategy_presets(DEFAULT_STRATEGY_PRESETS, sample_price_data())

    assert {"results", "failed_presets", "ranking"}.issubset(result)
    assert result["results"]
    assert result["failed_presets"] == []
    assert not result["ranking"].empty


def test_compare_strategy_presets_ranking_contains_key_columns():
    result = compare_strategy_presets(DEFAULT_STRATEGY_PRESETS, sample_price_data())

    expected_columns = {
        "preset_name",
        "total_return",
        "max_drawdown",
        "number_of_trades",
        "final_portfolio_value",
    }
    assert expected_columns.issubset(result["ranking"].columns)


def test_compare_strategy_presets_records_single_failed_preset():
    presets = {
        "trend_default": DEFAULT_STRATEGY_PRESETS["trend_default"],
        "bad_preset": {
            **DEFAULT_STRATEGY_PRESETS["trend_default"],
            "max_position_pct": 0,
        },
    }

    result = compare_strategy_presets(presets, sample_price_data())

    assert "trend_default" in result["results"]
    assert result["failed_presets"] == [{"name": "bad_preset", "error": "max_position_pct must be greater than 0 and less than or equal to 1."}]


def test_compare_strategy_presets_all_failed_returns_clear_result():
    presets = {
        "bad_preset_a": {**DEFAULT_STRATEGY_PRESETS["trend_default"], "max_position_pct": 0},
        "bad_preset_b": {**DEFAULT_STRATEGY_PRESETS["trend_default"], "rebalance_frequency": "yearly"},
    }

    result = compare_strategy_presets(presets, sample_price_data())

    assert result["results"] == {}
    assert len(result["failed_presets"]) == 2
    assert result["ranking"].empty


def test_compare_strategy_presets_rejects_empty_inputs():
    with pytest.raises(ValueError, match="presets"):
        compare_strategy_presets({}, sample_price_data())

    with pytest.raises(ValueError, match="price_data"):
        compare_strategy_presets(DEFAULT_STRATEGY_PRESETS, {})


def test_compare_strategy_presets_does_not_reference_external_trading_or_ai_clients():
    import src.strategies.comparison as comparison

    source = inspect.getsource(comparison)
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
    ]
    for word in forbidden:
        assert word not in source

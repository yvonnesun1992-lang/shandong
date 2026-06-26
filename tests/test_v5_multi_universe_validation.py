from __future__ import annotations

import numpy as np
import pandas as pd


def test_v5_multi_universe_validation_summarizes_each_universe():
    from quant_core_v5.validation_batch import run_validation_batch

    result = run_validation_batch(
        universes={
            "growth": _market_data({"AAPL": 0.55, "MSFT": 0.35, "NVDA": 0.45}),
            "defensive": _market_data({"JNJ": 0.12, "PG": 0.10, "KO": 0.08}),
        },
        factors=["momentum_20d", "trend_strength"],
        train_ratio=0.65,
        walk_forward_train_size=50,
        walk_forward_test_size=15,
        max_weight_per_asset=0.40,
        transaction_cost_bps=10.0,
        slippage_bps=5.0,
    )

    assert result["version"] == "V5.0-alpha-system"
    assert set(result["universes"]) == {"growth", "defensive"}
    assert result["summary"]["universe_count"] == 2
    assert 0 <= result["summary"]["profitable_test_ratio"] <= 1
    assert "average_test_return" in result["summary"]
    assert result["audit"]["broker_connection"] is False
    assert result["audit"]["real_trading"] is False


def test_v5_multi_universe_report_contains_commercial_summary():
    from quant_core_v5.validation_batch import format_batch_report, run_validation_batch

    result = run_validation_batch(
        universes={
            "growth": _market_data({"AAPL": 0.55, "MSFT": 0.35, "NVDA": 0.45}),
            "defensive": _market_data({"JNJ": 0.12, "PG": 0.10, "KO": 0.08}),
        },
        factors=["momentum_20d", "trend_strength"],
        train_ratio=0.65,
        walk_forward_train_size=50,
        walk_forward_test_size=15,
        max_weight_per_asset=0.40,
    )
    markdown = format_batch_report(result)

    assert "V5 Multi-Universe Validation Report" in markdown
    assert "growth" in markdown
    assert "defensive" in markdown
    assert "Profitable test ratio" in markdown
    assert "No broker connection" in markdown


def _market_data(drifts: dict[str, float], days: int = 120) -> dict[str, pd.DataFrame]:
    return {symbol: _frame(drift, days) for symbol, drift in drifts.items()}


def _frame(drift: float, days: int) -> pd.DataFrame:
    dates = pd.date_range("2023-01-01", periods=days, freq="D")
    close = 100 + np.arange(days) * drift + np.sin(np.arange(days) / 7) * 0.8
    return pd.DataFrame(
        {
            "datetime": dates,
            "open": close - 0.2,
            "high": close + 0.8,
            "low": close - 0.8,
            "close": close,
            "volume": 1000 + np.arange(days),
        }
    )

from __future__ import annotations

import numpy as np
import pandas as pd


def test_v5_validation_harness_splits_train_test_and_walk_forward():
    from quant_core_v5.validation import run_validation_harness

    result = run_validation_harness(
        market_data=_market_data(),
        factors=["momentum_20d", "trend_strength"],
        train_ratio=0.65,
        walk_forward_train_size=50,
        walk_forward_test_size=15,
        max_weight_per_asset=0.40,
        transaction_cost_bps=10.0,
        slippage_bps=5.0,
    )

    assert result["version"] == "V5.0-alpha-system"
    assert result["train"]["period"]["end"] < result["test"]["period"]["start"]
    assert result["train"]["summary"]["causal_backtest"] is True
    assert result["test"]["summary"]["causal_backtest"] is True
    assert len(result["walk_forward"]) >= 2
    assert result["audit"]["broker_connection"] is False
    assert result["audit"]["real_trading"] is False
    assert "profitable_test_period" in result["audit"]
    assert result["audit"]["transaction_cost_bps"] == 10.0
    assert result["audit"]["slippage_bps"] == 5.0


def test_v5_validation_report_markdown_contains_commercial_gates():
    from quant_core_v5.validation import format_validation_report, run_validation_harness

    result = run_validation_harness(
        market_data=_market_data(),
        factors=["momentum_20d", "trend_strength"],
        train_ratio=0.65,
        walk_forward_train_size=50,
        walk_forward_test_size=15,
        max_weight_per_asset=0.40,
        transaction_cost_bps=10.0,
        slippage_bps=5.0,
    )
    markdown = format_validation_report(result)

    assert "V5 Alpha Validation Report" in markdown
    assert "Train Period" in markdown
    assert "Test Period" in markdown
    assert "Walk-Forward" in markdown
    assert "No broker connection" in markdown
    assert "No profitability guarantee" in markdown
    assert "Transaction cost bps" in markdown
    assert "Gross total return" in markdown
    assert "Profitable window ratio" in markdown


def _market_data(days: int = 120) -> dict[str, pd.DataFrame]:
    return {
        "AAPL": _frame(0.55, days),
        "TSLA": _frame(0.20, days),
        "NVDA": _frame(0.35, days),
    }


def _frame(drift: float, days: int) -> pd.DataFrame:
    dates = pd.date_range("2023-01-01", periods=days, freq="D")
    close = 100 + np.arange(days) * drift + np.sin(np.arange(days) / 6) * 1.2
    return pd.DataFrame(
        {
            "datetime": dates,
            "open": close - 0.3,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": 1000 + np.arange(days),
        }
    )

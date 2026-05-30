import pandas as pd

from src.backtest.simple_backtest import run_simple_backtest


def test_backtest_uses_15_percent_position_cap():
    data = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=200),
            "open": range(1, 201),
            "high": range(2, 202),
            "low": range(0, 200),
            "close": range(1, 201),
            "volume": range(1000, 1200),
        }
    )

    result = run_simple_backtest(data, initial_cash=100_000)

    assert result["final_portfolio_value"] < 120_000

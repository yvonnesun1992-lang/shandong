from __future__ import annotations

import pandas as pd
import pytest

from src.backtest.portfolio_backtest import run_portfolio_backtest
from src.data.sample_data import load_sample_ohlcv


def sample_portfolio_data() -> dict[str, pd.DataFrame]:
    return {
        "NVDA": load_sample_ohlcv("us", "NVDA"),
        "300308": load_sample_ohlcv("cn", "300308"),
    }


def test_portfolio_backtest_runs_with_sample_data():
    result = run_portfolio_backtest(sample_portfolio_data())

    assert {"equity_curve", "trades", "summary"}.issubset(result)
    assert not result["equity_curve"].empty
    assert result["summary"]["final_portfolio_value"] > 0
    assert result["summary"]["number_of_trades"] == len(result["trades"])


def test_portfolio_backtest_keeps_cash_non_negative():
    result = run_portfolio_backtest(sample_portfolio_data(), initial_cash=100_000)

    assert result["equity_curve"]["cash"].ge(-0.000001).all()


def test_portfolio_backtest_respects_position_cap():
    result = run_portfolio_backtest(sample_portfolio_data(), initial_cash=100_000, max_position_pct=0.15)
    buy_trades = result["trades"][result["trades"]["action"] == "BUY"]

    assert buy_trades["amount"].le(15_000.01).all()


def test_portfolio_backtest_skips_short_data():
    data = sample_portfolio_data()
    data["SHORT"] = data["NVDA"].head(50)

    result = run_portfolio_backtest(data)

    assert "SHORT" in result["skipped_symbols"]


def test_portfolio_backtest_rejects_empty_price_data():
    with pytest.raises(ValueError, match="price_data"):
        run_portfolio_backtest({})


def test_portfolio_backtest_does_not_reference_broker_or_order_clients():
    import src.backtest.portfolio_backtest as portfolio_backtest

    source = portfolio_backtest.run_portfolio_backtest.__code__.co_names

    forbidden = {"IBKR", "Alpaca", "Robinhood", "place_order", "broker_order"}
    assert forbidden.isdisjoint(set(source))

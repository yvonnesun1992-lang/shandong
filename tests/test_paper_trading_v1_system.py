from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def sample_prices(days: int = 90, start: float = 100.0, step: float = 1.0) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=days, freq="D")
    close = start + np.arange(days) * step
    return pd.DataFrame(
        {
            "datetime": dates,
            "open": close - 0.5,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.arange(days) + 1000,
        }
    )


def test_data_loader_standardizes_yfinance_data_and_uses_cache(tmp_path, monkeypatch):
    from data.data_loader import DataLoader

    raw = pd.DataFrame(
        {
            "Open": [10.0, np.nan, 12.0],
            "High": [11.0, 12.0, 13.0],
            "Low": [9.0, 10.0, 11.0],
            "Close": [10.5, np.nan, 12.5],
            "Volume": [100, 200, 300],
        },
        index=pd.to_datetime(["2024-01-03", "2024-01-01", "2024-01-02"]),
    )

    calls = {"count": 0}

    def fake_download(*args, **kwargs):
        calls["count"] += 1
        return raw

    monkeypatch.setattr("data.data_loader.yf.download", fake_download)

    loader = DataLoader(cache_dir=tmp_path)
    first = loader.get_history("AAPL", start="2024-01-01", end="2024-01-05")
    second = loader.get_history("AAPL", start="2024-01-01", end="2024-01-05")

    assert calls["count"] == 1
    assert list(first.columns) == ["datetime", "open", "high", "low", "close", "volume"]
    assert first["datetime"].is_monotonic_increasing
    assert not first[["open", "high", "low", "close", "volume"]].isna().any().any()
    pd.testing.assert_frame_equal(first, second)


def test_strategies_generate_expected_signals():
    from strategies.ma_crossover import MACrossoverStrategy
    from strategies.mean_reversion import MeanReversionStrategy
    from strategies.momentum import MomentumStrategy

    up = sample_prices(step=1.0)
    down = sample_prices(step=-1.0)
    dip = sample_prices(days=40, step=0.0)
    dip.loc[len(dip) - 1, "close"] = 80.0

    ma_signal = MACrossoverStrategy().generate_signal(up, "AAPL")
    momentum_signal = MomentumStrategy(threshold=0.02).generate_signal(up, "NVDA")
    mean_reversion_signal = MeanReversionStrategy(window=20, num_std=1.5).generate_signal(dip, "TSLA")
    sell_signal = MomentumStrategy(threshold=0.02).generate_signal(down, "MSFT")

    assert ma_signal["action"] == "BUY"
    assert momentum_signal["action"] == "BUY"
    assert mean_reversion_signal["action"] == "BUY"
    assert sell_signal["action"] == "SELL"
    assert 0 <= ma_signal["strength"] <= 1
    assert ma_signal["timestamp"] == up["datetime"].iloc[-1]


def test_signal_engine_deduplicates_conflicts_and_emits_hold_when_empty():
    from signals.signal_engine import SignalEngine

    engine = SignalEngine()
    signals = [
        {"symbol": "AAPL", "action": "BUY", "strength": 0.3, "timestamp": "t1"},
        {"symbol": "AAPL", "action": "SELL", "strength": 0.8, "timestamp": "t1"},
        {"symbol": "MSFT", "action": "HOLD", "strength": 0.1, "timestamp": "t1"},
        {"symbol": "MSFT", "action": "BUY", "strength": 0.4, "timestamp": "t1"},
    ]

    merged = engine.merge_signals(signals)
    by_symbol = {item["symbol"]: item for item in merged}

    assert by_symbol["AAPL"]["action"] == "SELL"
    assert by_symbol["AAPL"]["strength"] == 0.8
    assert by_symbol["MSFT"]["action"] == "BUY"
    assert engine.merge_signals([], symbols=["AAPL"])[0]["action"] == "HOLD"


def test_paper_broker_executes_orders_without_negative_cash_or_lost_positions():
    from broker.paper_broker import PaperBroker

    broker = PaperBroker(initial_cash=100_000)
    buy = broker.place_order("AAPL", "BUY", price=100.0, shares=100)
    sell = broker.place_order("AAPL", "SELL", price=110.0, shares=40)
    rejected = broker.place_order("TSLA", "BUY", price=1_000_000.0, shares=1)
    oversell = broker.place_order("AAPL", "SELL", price=110.0, shares=1000)
    portfolio = broker.update_portfolio({"AAPL": 110.0})

    assert buy["status"] == "FILLED"
    assert sell["status"] == "FILLED"
    assert rejected["status"] == "REJECTED"
    assert oversell["status"] == "REJECTED"
    assert broker.cash >= 0
    assert broker.positions["AAPL"] == 60
    assert portfolio["cash"] == broker.cash
    assert portfolio["holdings"]["AAPL"]["shares"] == 60
    assert portfolio["total_equity"] > broker.cash
    assert len(broker.trades) == 2


def test_backtest_engine_outputs_metrics_and_equity_curve_without_nan():
    from backtest.engine import BacktestEngine
    from strategies.ma_crossover import MACrossoverStrategy

    data = sample_prices(days=120, step=0.8)
    result = BacktestEngine(initial_cash=100_000).run(data, MACrossoverStrategy(), "AAPL")

    assert result["metrics"]["number_of_trades"] >= 1
    assert {"total_return", "annual_return", "max_drawdown", "sharpe_ratio", "win_rate", "number_of_trades"} <= set(result["metrics"])
    assert not result["equity_curve"]["total_equity"].isna().any()
    assert result["equity_curve"]["total_equity"].iloc[-1] > 0
    assert result["metrics"]["max_drawdown"] >= 0


def test_visualization_functions_return_figures():
    from visualization.chart import plot_drawdown_curve, plot_equity_curve, plot_strategy_comparison, plot_trade_markers

    equity = pd.DataFrame(
        {
            "datetime": pd.date_range("2024-01-01", periods=5),
            "total_equity": [100, 105, 103, 108, 110],
        }
    )
    trades = pd.DataFrame(
        {
            "timestamp": [pd.Timestamp("2024-01-02")],
            "symbol": ["AAPL"],
            "action": ["BUY"],
            "price": [101.0],
            "shares": [10],
        }
    )

    assert plot_equity_curve(equity) is not None
    assert plot_drawdown_curve(equity) is not None
    assert plot_trade_markers(sample_prices(days=5), trades, "AAPL") is not None
    assert plot_strategy_comparison({"ma": equity, "momentum": equity}) is not None

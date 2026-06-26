from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
from fastapi.testclient import TestClient


def test_live_signal_generation_uses_v5_alpha_without_future_rows():
    from live.data_stream import HistoricalReplayStream
    from live.signal_engine import LiveSignalEngine

    stream = HistoricalReplayStream(_market_data(["AAPL", "MSFT", "JPM"]), buffer_size=90)
    engine = LiveSignalEngine(min_history=45)
    signals = []
    for event in stream:
        signals = engine.on_market_event(event)
        if signals:
            break

    assert signals
    assert {signal["action"] for signal in signals}.issubset({"BUY", "SELL", "HOLD"})
    assert all(signal["timestamp"] == event.timestamp for signal in signals)
    assert engine.last_signal_timestamp == event.timestamp
    assert engine.last_history_end == event.timestamp
    assert engine.last_history_end <= event.timestamp


def test_risk_kill_switch_blocks_orders_after_drawdown():
    from risk.risk_engine_v2 import RiskEngineV2

    risk = RiskEngineV2(max_drawdown=0.05, max_daily_loss=0.10)
    risk.update_equity(100_000, pd.Timestamp("2026-01-01 09:30"))
    risk.update_equity(93_000, pd.Timestamp("2026-01-01 10:00"))

    assert risk.kill_switch_active is True
    decision = risk.validate_order({"symbol": "AAPL", "action": "BUY", "quantity": 10, "price": 100}, {"equity": 93_000})
    assert decision["approved"] is False
    assert decision["reason"] == "KILL_SWITCH_ACTIVE"


def test_execution_latency_and_paper_fill():
    from execution.execution_engine import ExecutionEngine

    engine = ExecutionEngine(latency_steps=2, slippage_bps=10)
    timestamp = pd.Timestamp("2026-01-01 09:30")
    engine.submit_order({"symbol": "AAPL", "action": "BUY", "quantity": 5, "price": 100, "timestamp": timestamp})

    assert engine.process_market_tick({"AAPL": 100}, timestamp + timedelta(minutes=1)) == []
    fills = engine.process_market_tick({"AAPL": 101}, timestamp + timedelta(minutes=2))

    assert len(fills) == 1
    assert fills[0]["symbol"] == "AAPL"
    assert fills[0]["action"] == "BUY"
    assert fills[0]["fill_price"] > 101
    assert fills[0]["paper_trading"] is True


def test_portfolio_consistency_after_fills_and_prices():
    from portfolio.portfolio_engine import PortfolioEngine

    portfolio = PortfolioEngine(initial_cash=10_000)
    portfolio.apply_fill({"symbol": "AAPL", "action": "BUY", "quantity": 10, "fill_price": 100, "timestamp": pd.Timestamp("2026-01-01")})
    snapshot = portfolio.mark_to_market({"AAPL": 110}, pd.Timestamp("2026-01-01 09:31"))

    assert snapshot["cash"] == 9_000
    assert snapshot["positions"]["AAPL"]["quantity"] == 10
    assert snapshot["equity"] == 10_100
    assert snapshot["unrealized_pnl"] == 100


def test_streaming_pipeline_updates_monitoring_and_api_endpoints():
    from live.pipeline import LiveTradingPipeline
    from src.api.v2.server import create_v2_api_app

    pipeline = LiveTradingPipeline(
        market_data=_market_data(["AAPL", "MSFT", "JPM", "XOM", "JNJ"]),
        initial_cash=100_000,
        min_history=55,
        latency_steps=1,
    )
    result = pipeline.run(max_steps=80)

    assert result["status"] == "running"
    assert result["portfolio"]["equity"] > 0
    assert result["monitoring"]["signal_count"] > 0
    assert result["safety"]["broker_connection"] is False
    assert result["safety"]["real_trading"] is False

    client = TestClient(create_v2_api_app())
    live_status = client.get("/api/v5/live_status").json()
    pnl = client.get("/api/v5/pnl").json()
    positions = client.get("/api/v5/positions").json()
    signals = client.get("/api/v5/signals").json()

    assert live_status["success"] is True
    assert pnl["success"] is True
    assert positions["success"] is True
    assert signals["success"] is True
    assert "live_status" in live_status["data"]
    assert "pnl" in pnl["data"]
    assert "positions" in positions["data"]
    assert "signals" in signals["data"]


def _market_data(symbols: list[str], days: int = 120) -> dict[str, pd.DataFrame]:
    return {symbol: _frame(i, days) for i, symbol in enumerate(symbols)}


def _frame(offset: int, days: int) -> pd.DataFrame:
    start = datetime(2026, 1, 1, 9, 30)
    timestamps = [start + timedelta(minutes=i) for i in range(days)]
    base = 100 + offset * 5
    close = [base + i * (0.08 + offset * 0.01) + ((i % 9) - 4) * 0.05 for i in range(days)]
    return pd.DataFrame(
        {
            "datetime": timestamps,
            "open": [value - 0.1 for value in close],
            "high": [value + 0.4 for value in close],
            "low": [value - 0.4 for value in close],
            "close": close,
            "volume": [1000 + i for i in range(days)],
        }
    )

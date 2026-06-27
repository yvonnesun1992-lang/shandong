from __future__ import annotations

import pandas as pd


def test_runtime_loop_runs_and_updates_portfolio():
    from runtime.market_simulator import MarketSimulator
    from runtime.trading_engine import TradingEngine

    engine = TradingEngine(
        market=MarketSimulator(_bars()),
        signal_generator=_signal_generator,
        initial_cash=50_000,
    )
    result = engine.run(max_ticks=20)

    assert result["status"] == "STOPPED"
    assert result["ticks_processed"] == 20
    assert result["monitor"]["signal_count"] > 0
    assert result["monitor"]["trade_count"] > 0
    assert result["state"]["cash"] <= 50_000
    assert result["pnl"]["equity"] > 0
    assert result["safety"]["broker_connection"] is False
    assert result["safety"]["real_trading"] is False


def test_event_flow_records_market_signal_order_fill_and_position_events():
    from runtime.market_simulator import MarketSimulator
    from runtime.trading_engine import TradingEngine

    engine = TradingEngine(MarketSimulator(_bars()), signal_generator=_signal_generator, initial_cash=50_000)
    engine.run(max_ticks=15)
    event_types = [event.type for event in engine.event_bus.events]

    assert "MARKET_TICK" in event_types
    assert "SIGNAL_GENERATED" in event_types
    assert "ORDER_PLACED" in event_types
    assert "ORDER_FILLED" in event_types
    assert "POSITION_UPDATED" in event_types


def test_risk_kill_switch_stops_new_orders():
    from runtime.market_simulator import MarketSimulator
    from runtime.trading_engine import TradingEngine

    engine = TradingEngine(
        market=MarketSimulator(_bars([100, 101, 102, 80, 70, 65, 64, 63])),
        signal_generator=_always_buy_signal,
        initial_cash=50_000,
        max_drawdown=0.02,
    )
    result = engine.run(max_ticks=8)

    assert result["risk"]["kill_switch_active"] is True
    assert any(event.type == "RISK_TRIGGERED" for event in engine.event_bus.events)


def test_portfolio_update_consistency_matches_account_state():
    from runtime.market_simulator import MarketSimulator
    from runtime.trading_engine import TradingEngine

    engine = TradingEngine(MarketSimulator(_bars()), signal_generator=_signal_generator, initial_cash=50_000)
    result = engine.run(max_ticks=12)

    state = result["state"]
    pnl = result["pnl"]
    assert round(state["equity"], 6) == round(pnl["equity"], 6)
    assert round(state["cash"] + state["position_value"], 6) == round(state["equity"], 6)


def test_pnl_realtime_tracks_equity_curve_and_drawdown():
    from runtime.pnl_engine import PnLEngine

    pnl = PnLEngine()
    pnl.update({"equity": 100_000, "cash": 100_000, "position_value": 0}, pd.Timestamp("2026-01-01"))
    pnl.update({"equity": 105_000, "cash": 50_000, "position_value": 55_000}, pd.Timestamp("2026-01-02"))
    pnl.update({"equity": 99_000, "cash": 50_000, "position_value": 49_000}, pd.Timestamp("2026-01-03"))

    snapshot = pnl.snapshot()
    assert len(snapshot["equity_curve"]) == 3
    assert snapshot["unrealized_pnl"] == -1_000
    assert round(snapshot["drawdown"], 4) == 0.0571


def test_system_controller_pause_resume_and_emergency_stop():
    from runtime.market_simulator import MarketSimulator
    from runtime.system_controller import SystemController
    from runtime.trading_engine import TradingEngine

    controller = SystemController(TradingEngine(MarketSimulator(_bars()), signal_generator=_signal_generator))
    controller.start_engine(max_ticks=3)
    controller.pause_engine()
    assert controller.status == "PAUSED"
    controller.resume_engine()
    assert controller.status == "RUNNING"
    controller.emergency_stop()
    assert controller.status == "STOPPED"
    assert controller.engine.risk_gate.kill_switch_active is True


def _signal_generator(tick, state):
    return {
        "symbol": tick["symbol"],
        "action": "BUY" if tick["close"] >= 100 else "HOLD",
        "strength": 0.5,
        "timestamp": tick["datetime"],
    }


def _always_buy_signal(tick, state):
    return {
        "symbol": tick["symbol"],
        "action": "BUY",
        "strength": 1.0,
        "timestamp": tick["datetime"],
    }


def _bars(prices: list[float] | None = None) -> pd.DataFrame:
    values = prices or [100 + idx * 0.5 for idx in range(40)]
    dates = pd.date_range("2026-01-01 09:30", periods=len(values), freq="min")
    return pd.DataFrame(
        {
            "datetime": dates,
            "symbol": ["AAPL"] * len(values),
            "open": values,
            "high": [value + 0.2 for value in values],
            "low": [value - 0.2 for value in values],
            "close": values,
            "volume": [1000 + idx for idx in range(len(values))],
        }
    )

from __future__ import annotations

import json

import pandas as pd


def test_watchdog_restart_when_crash_or_lag_detected():
    from runtime.watchdog import Watchdog

    engine = _RestartableEngine()
    watchdog = Watchdog(max_event_loop_delay_ms=100, max_signal_latency_ms=50)
    result = watchdog.check(
        engine,
        metrics={"event_loop_delay_ms": 250, "signal_latency_ms": 10, "cpu_usage": 0.2, "memory_usage_mb": 128},
    )

    assert result["status"] == "RESTARTED"
    assert result["reason"] == "EVENT_LOOP_DELAY"
    assert engine.restart_count == 1


def test_state_checkpoint_save_and_restore(tmp_path):
    from runtime.state_checkpoint import StateCheckpoint

    checkpoint = StateCheckpoint(tmp_path / "runtime_state.json")
    state = {
        "portfolio": {"cash": 12_000, "equity": 12_500},
        "positions": {"AAPL": {"quantity": 5}},
        "pnl": {"equity": 12_500},
        "open_orders": [{"order_id": "PAPER-1"}],
    }

    path = checkpoint.save(state, force=True)
    restored = checkpoint.load_latest()

    assert path.exists()
    assert restored["portfolio"]["cash"] == 12_000
    assert restored["positions"]["AAPL"]["quantity"] == 5
    assert restored["open_orders"][0]["order_id"] == "PAPER-1"


def test_recovery_engine_restores_portfolio_state(tmp_path):
    from runtime.recovery_engine import RecoveryEngine
    from runtime.state_checkpoint import StateCheckpoint
    from trading.paper_account import PaperAccount

    checkpoint = StateCheckpoint(tmp_path / "state.json")
    checkpoint.save(
        {
            "portfolio": {"cash": 8_000, "realized_pnl": 123},
            "positions": {"MSFT": {"quantity": 3, "avg_price": 200}},
            "open_orders": [{"order_id": "PAPER-2"}],
        },
        force=True,
    )
    account = PaperAccount(initial_cash=10_000)
    result = RecoveryEngine(checkpoint).restore_account(account)

    assert result["restored"] is True
    assert account.cash == 8_000
    assert account.positions["MSFT"]["quantity"] == 3
    assert result["open_orders"][0]["order_id"] == "PAPER-2"


def test_mode_manager_switches_to_safe_mode_on_error_burst_and_drawdown():
    from runtime.mode_manager import ModeManager

    manager = ModeManager(error_threshold=2, drawdown_threshold=0.10)
    manager.record_error("first")
    manager.record_error("second")

    assert manager.mode == "SAFE_MODE"

    manager = ModeManager(error_threshold=5, drawdown_threshold=0.10)
    manager.evaluate_risk({"drawdown": 0.12})
    assert manager.mode == "SAFE_MODE"


def test_engine_crash_recovery_logs_error_and_enters_safe_mode(tmp_path):
    from runtime.error_handler import ErrorHandler
    from runtime.logger import ProductionLogger
    from runtime.market_simulator import MarketSimulator
    from runtime.mode_manager import ModeManager
    from runtime.state_checkpoint import StateCheckpoint
    from runtime.trading_engine import TradingEngine

    logger = ProductionLogger(tmp_path / "runtime.jsonl")
    mode_manager = ModeManager(error_threshold=1)
    engine = TradingEngine(
        MarketSimulator(_bars()),
        signal_generator=_crashing_signal_generator,
        error_handler=ErrorHandler(logger=logger, mode_manager=mode_manager),
        mode_manager=mode_manager,
        state_checkpoint=StateCheckpoint(tmp_path / "checkpoint.json"),
    )
    result = engine.run(max_ticks=5)

    assert result["status"] == "STOPPED"
    assert result["mode"] == "SAFE_MODE"
    assert result["monitor"]["error_count"] >= 1
    assert result["health"]["status"] in {"DEGRADED", "FAILED"}
    assert (tmp_path / "checkpoint.json").exists()
    log_lines = [json.loads(line) for line in (tmp_path / "runtime.jsonl").read_text(encoding="utf-8").splitlines()]
    assert any(line["event_type"] == "ERROR" for line in log_lines)
    assert not any("secret" in json.dumps(line).lower() for line in log_lines)


def test_health_monitor_reports_degraded_for_errors_and_latency():
    from runtime.health_monitor import HealthMonitor

    monitor = HealthMonitor(max_execution_latency_ms=50, max_signal_delay_ms=50)
    result = monitor.update(
        engine_alive=True,
        execution_latency_ms=120,
        signal_delay_ms=10,
        memory_usage_mb=256,
        error_count=1,
    )

    assert result["status"] == "DEGRADED"
    assert result["latency"]["execution_ms"] == 120
    assert result["errors"] == 1


class _RestartableEngine:
    def __init__(self) -> None:
        self.restart_count = 0

    def restart_engine(self) -> None:
        self.restart_count += 1


def _crashing_signal_generator(tick, state):
    if tick["close"] >= 101:
        raise RuntimeError("simulated runtime failure")
    return {
        "symbol": tick["symbol"],
        "action": "BUY",
        "strength": 0.5,
        "timestamp": tick["datetime"],
    }


def _bars() -> pd.DataFrame:
    prices = [100, 101, 102, 103, 104, 105]
    dates = pd.date_range("2026-01-01 09:30", periods=len(prices), freq="min")
    return pd.DataFrame(
        {
            "datetime": dates,
            "symbol": ["AAPL"] * len(prices),
            "open": prices,
            "high": [price + 0.2 for price in prices],
            "low": [price - 0.2 for price in prices],
            "close": prices,
            "volume": [1000 + idx for idx in range(len(prices))],
        }
    )

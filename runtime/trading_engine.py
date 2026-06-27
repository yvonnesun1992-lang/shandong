from __future__ import annotations

from time import perf_counter

from runtime.error_handler import ErrorHandler
from runtime.event_bus import EventBus
from runtime.health_monitor import HealthMonitor
from runtime.market_simulator import MarketSimulator
from runtime.mode_manager import ModeManager
from runtime.monitor import RuntimeMonitor
from runtime.pnl_engine import PnLEngine
from runtime.risk_gate import RiskGate
from runtime.state_manager import StateManager
from runtime.state_checkpoint import StateCheckpoint
from runtime.watchdog import Watchdog
from trading.paper_broker import PaperBroker
from trading.risk_limits import RiskLimits
from trading.signal_to_order import SignalToOrderConverter


class TradingEngine:
    def __init__(
        self,
        market: MarketSimulator,
        signal_generator,
        initial_cash: float = 100_000.0,
        max_drawdown: float = 0.10,
        watchdog: Watchdog | None = None,
        state_checkpoint: StateCheckpoint | None = None,
        health_monitor: HealthMonitor | None = None,
        error_handler: ErrorHandler | None = None,
        mode_manager: ModeManager | None = None,
    ) -> None:
        self.market = market
        self.signal_generator = signal_generator
        self.broker = PaperBroker(initial_cash=initial_cash)
        self.event_bus = EventBus()
        self.state_manager = StateManager(self.broker.account)
        self.pnl_engine = PnLEngine()
        self.risk_gate = RiskGate(RiskLimits(max_drawdown=max_drawdown), self.event_bus)
        self.converter = SignalToOrderConverter()
        self.monitor = RuntimeMonitor()
        self.watchdog = watchdog or Watchdog()
        self.state_checkpoint = state_checkpoint or StateCheckpoint()
        self.health_monitor = health_monitor or HealthMonitor()
        self.mode_manager = mode_manager or ModeManager()
        self.error_handler = error_handler or ErrorHandler(mode_manager=self.mode_manager)
        self.status = "IDLE"
        self.ticks_processed = 0
        self.last_execution_latency_ms = 0.0
        self.last_signal_delay_ms = 0.0

    def run(self, max_ticks: int | None = None) -> dict:
        self.status = "RUNNING"
        self.market.open_market()
        while self.market.market_is_open():
            if max_ticks is not None and self.ticks_processed >= max_ticks:
                break
            tick = self.market.get_latest()
            if tick is None:
                break
            try:
                self._process_tick(tick)
            except Exception as exc:
                self.monitor.error_count += 1
                self.error_handler.handle(exc, {"tick": tick, "tick_index": self.ticks_processed})
            self.ticks_processed += 1
            self.watchdog.check(
                self,
                {
                    "event_loop_delay_ms": 0.0,
                    "signal_latency_ms": self.last_signal_delay_ms,
                    "memory_usage_mb": self.health_monitor.snapshot().get("memory", {}).get("usage_mb", 0.0),
                },
            )
            self.health_monitor.update(
                engine_alive=self.status == "RUNNING",
                execution_latency_ms=self.last_execution_latency_ms,
                signal_delay_ms=self.last_signal_delay_ms,
                error_count=self.error_handler.error_count,
            )
            self.state_checkpoint.save(self._checkpoint_state())
            if self.risk_gate.kill_switch_active:
                break
        self.market.close_market()
        self.status = "STOPPED"
        self.health_monitor.update(
            engine_alive=True,
            execution_latency_ms=self.last_execution_latency_ms,
            signal_delay_ms=self.last_signal_delay_ms,
            error_count=self.error_handler.error_count,
        )
        self.state_checkpoint.save(self._checkpoint_state(), force=True)
        return self.snapshot()

    def _process_tick(self, tick: dict) -> None:
        symbol = str(tick.get("symbol", "AAPL")).upper()
        price = float(tick["close"])
        timestamp = tick["datetime"]
        self.event_bus.publish("MARKET_TICK", {"symbol": symbol, "price": price, "timestamp": timestamp})
        state = self.state_manager.update_price(symbol, price)
        signal_started = perf_counter()
        signal = self.signal_generator(tick, state)
        self.last_signal_delay_ms = (perf_counter() - signal_started) * 1000
        if signal:
            self.monitor.record_signal()
            self.event_bus.publish("SIGNAL_GENERATED", signal)
        order = self.converter.convert(signal or {}, self.broker.account, price)
        if order is not None:
            decision = self.risk_gate.pre_trade_check(order, self.broker.account, price)
            if decision["approved"]:
                self.state_manager.add_order(order)
                self.event_bus.publish("ORDER_PLACED", {"order_id": order.order_id, "symbol": order.symbol, "side": order.side})
                started = perf_counter()
                execution = self.broker.execute_order(order, price)
                latency_ms = (perf_counter() - started) * 1000
                self.last_execution_latency_ms = latency_ms
                if execution.status == "FILLED":
                    self.state_manager.add_trade(execution)
                    self.monitor.record_execution(latency_ms)
                    self.event_bus.publish("ORDER_FILLED", execution.as_dict())
        self.state_manager.update_price(symbol, price)
        summary = self.broker.get_account_summary()
        risk = self.risk_gate.post_trade_validation(summary)
        self.mode_manager.evaluate_risk(risk)
        pnl = self.pnl_engine.update(summary, timestamp)
        state = self.state_manager.snapshot()
        self.event_bus.publish("POSITION_UPDATED", {"symbol": symbol, "state": state, "risk": risk})
        self.monitor.update_state(state, pnl)

    def snapshot(self) -> dict:
        state = self.state_manager.snapshot()
        pnl = self.pnl_engine.snapshot()
        return {
            "status": self.status,
            "ticks_processed": self.ticks_processed,
            "state": state,
            "pnl": pnl,
            "risk": {"kill_switch_active": self.risk_gate.kill_switch_active},
            "monitor": self.monitor.snapshot(),
            "health": self.health_monitor.snapshot(),
            "mode": self.mode_manager.mode,
            "safety": {
                "broker_connection": False,
                "real_trading": False,
                "real_account": False,
                "payment": False,
            },
        }

    def restart_engine(self) -> None:
        self.status = "RESTARTING"
        self.status = "RUNNING"

    def _checkpoint_state(self) -> dict:
        state = self.state_manager.snapshot()
        return {
            "portfolio": {
                "cash": state.get("cash", 0.0),
                "equity": state.get("equity", 0.0),
                "realized_pnl": state.get("realized_pnl", 0.0),
            },
            "positions": state.get("positions", {}),
            "pnl": self.pnl_engine.snapshot(),
            "open_orders": state.get("active_orders", []),
            "mode": self.mode_manager.mode,
            "health": self.health_monitor.snapshot(),
        }

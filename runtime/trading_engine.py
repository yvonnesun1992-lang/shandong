from __future__ import annotations

from time import perf_counter

from runtime.event_bus import EventBus
from runtime.market_simulator import MarketSimulator
from runtime.monitor import RuntimeMonitor
from runtime.pnl_engine import PnLEngine
from runtime.risk_gate import RiskGate
from runtime.state_manager import StateManager
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
        self.status = "IDLE"
        self.ticks_processed = 0

    def run(self, max_ticks: int | None = None) -> dict:
        self.status = "RUNNING"
        self.market.open_market()
        while self.market.market_is_open():
            if max_ticks is not None and self.ticks_processed >= max_ticks:
                break
            tick = self.market.get_latest()
            if tick is None:
                break
            self._process_tick(tick)
            self.ticks_processed += 1
            if self.risk_gate.kill_switch_active:
                break
        self.market.close_market()
        self.status = "STOPPED"
        return self.snapshot()

    def _process_tick(self, tick: dict) -> None:
        symbol = str(tick.get("symbol", "AAPL")).upper()
        price = float(tick["close"])
        timestamp = tick["datetime"]
        self.event_bus.publish("MARKET_TICK", {"symbol": symbol, "price": price, "timestamp": timestamp})
        state = self.state_manager.update_price(symbol, price)
        signal = self.signal_generator(tick, state)
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
                if execution.status == "FILLED":
                    self.state_manager.add_trade(execution)
                    self.monitor.record_execution(latency_ms)
                    self.event_bus.publish("ORDER_FILLED", execution.as_dict())
        self.state_manager.update_price(symbol, price)
        summary = self.broker.get_account_summary()
        risk = self.risk_gate.post_trade_validation(summary)
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
            "safety": {
                "broker_connection": False,
                "real_trading": False,
                "real_account": False,
                "payment": False,
            },
        }



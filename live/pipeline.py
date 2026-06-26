from __future__ import annotations

from execution.execution_engine import ExecutionEngine
from live.data_stream import HistoricalReplayStream
from live.signal_engine import LiveSignalEngine
from monitoring.system_monitor import SystemMonitor
from portfolio.portfolio_engine import PortfolioEngine
from risk.risk_engine_v2 import RiskEngineV2


LATEST_LIVE_STATE: dict = {}


class LiveTradingPipeline:
    def __init__(
        self,
        market_data: dict,
        initial_cash: float = 100_000.0,
        min_history: int = 80,
        latency_steps: int = 1,
    ) -> None:
        self.stream = HistoricalReplayStream(market_data, buffer_size=max(min_history + 20, 120))
        self.signal_engine = LiveSignalEngine(min_history=min_history, max_weight_per_asset=0.40)
        self.risk_engine = RiskEngineV2(max_position_exposure=0.20, max_daily_loss=0.05, max_drawdown=0.15)
        self.execution_engine = ExecutionEngine(latency_steps=latency_steps, slippage_bps=5.0)
        self.portfolio = PortfolioEngine(initial_cash=initial_cash)
        self.monitor = SystemMonitor()

    def run(self, max_steps: int | None = None) -> dict:
        last_snapshot = self.portfolio.snapshot()
        for step, event in enumerate(self.stream):
            if max_steps is not None and step >= max_steps:
                break
            prices = {symbol: float(bar["close"]) for symbol, bar in event.bars.items()}
            fills = self.execution_engine.process_market_tick(prices, event.timestamp)
            for fill in fills:
                self.portfolio.apply_fill(fill)
            snapshot = self.portfolio.mark_to_market(prices, event.timestamp)
            self.risk_engine.update_equity(snapshot["equity"], event.timestamp)
            signals = self.signal_engine.on_market_event(event)
            self.monitor.record_signals(signals)
            self.monitor.record_fills(fills)
            self.monitor.record_portfolio(snapshot)
            for signal in signals:
                if signal["action"] not in {"BUY", "SELL"}:
                    continue
                price = prices.get(signal["symbol"])
                if price is None:
                    continue
                quantity = max(1.0, snapshot["equity"] * 0.02 * min(signal["strength"], 1.0) / price)
                order = {
                    "symbol": signal["symbol"],
                    "action": signal["action"],
                    "quantity": quantity,
                    "price": price,
                    "timestamp": event.timestamp,
                }
                decision = self.risk_engine.validate_order(order, snapshot, regime=signal.get("regime", "sideways"))
                if decision["approved"]:
                    order["quantity"] *= decision.get("scale", 1.0)
                    self.execution_engine.submit_order(order)
            last_snapshot = snapshot
        state = {
            "status": "running",
            "portfolio": last_snapshot,
            "positions": last_snapshot.get("positions", {}),
            "monitoring": self.monitor.dashboard_data(),
            "signals": self.monitor.signal_log[-50:],
            "trades": self.monitor.trades_log[-50:],
            "safety": {
                "broker_connection": False,
                "real_trading": False,
                "paper_trading": True,
                "auto_order_routing": False,
            },
        }
        LATEST_LIVE_STATE.clear()
        LATEST_LIVE_STATE.update(state)
        return state


def get_live_state() -> dict:
    if not LATEST_LIVE_STATE:
        return {
            "status": "idle",
            "portfolio": {"cash": 0.0, "equity": 0.0, "positions": {}},
            "positions": {},
            "monitoring": {
                "equity_curve": [],
                "drawdown_curve": [],
                "exposure_curve": [],
                "signal_count": 0,
                "trade_count": 0,
                "error_count": 0,
                "regime_state": {"state": "unknown", "confidence": 0.0},
            },
            "signals": [],
            "trades": [],
            "safety": {"broker_connection": False, "real_trading": False, "paper_trading": True},
        }
    return dict(LATEST_LIVE_STATE)

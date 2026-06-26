from __future__ import annotations

from collections import deque

import pandas as pd


class ExecutionEngine:
    def __init__(self, latency_steps: int = 1, slippage_bps: float = 5.0) -> None:
        self.latency_steps = max(0, int(latency_steps))
        self.slippage_bps = float(slippage_bps)
        self._queue: deque[dict] = deque()
        self.trade_log: list[dict] = []

    def submit_order(self, order: dict) -> dict:
        queued = dict(order)
        queued["remaining_steps"] = self.latency_steps
        queued["paper_trading"] = True
        self._queue.append(queued)
        return queued

    def process_market_tick(self, prices: dict[str, float], timestamp) -> list[dict]:
        fills = []
        pending = deque()
        while self._queue:
            order = self._queue.popleft()
            order["remaining_steps"] = int(order.get("remaining_steps", 0)) - 1
            if order["remaining_steps"] > 0:
                pending.append(order)
                continue
            symbol = order["symbol"]
            if symbol not in prices:
                pending.append(order)
                continue
            fill = self._fill_order(order, float(prices[symbol]), pd.Timestamp(timestamp))
            fills.append(fill)
            self.trade_log.append(fill)
        self._queue = pending
        return fills

    def queued_orders(self) -> list[dict]:
        return list(self._queue)

    def _fill_order(self, order: dict, market_price: float, timestamp: pd.Timestamp) -> dict:
        side = 1 if order.get("action") == "BUY" else -1
        fill_price = market_price * (1 + side * self.slippage_bps / 10_000)
        return {
            "symbol": order["symbol"],
            "action": order["action"],
            "quantity": float(order.get("quantity", 0.0)),
            "requested_price": float(order.get("price", market_price)),
            "fill_price": float(fill_price),
            "timestamp": timestamp,
            "paper_trading": True,
            "latency_steps": self.latency_steps,
        }

from __future__ import annotations

import pandas as pd


class PortfolioEngine:
    def __init__(self, initial_cash: float = 100_000.0) -> None:
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        self.positions: dict[str, dict] = {}
        self.equity_curve: list[dict] = []

    def apply_fill(self, fill: dict) -> dict:
        symbol = str(fill["symbol"])
        quantity = float(fill.get("quantity", 0.0))
        price = float(fill.get("fill_price", 0.0))
        action = str(fill.get("action", "HOLD"))
        current = self.positions.setdefault(symbol, {"quantity": 0.0, "avg_price": 0.0})
        if action == "BUY":
            cost = quantity * price
            if cost > self.cash:
                quantity = self.cash / price if price > 0 else 0.0
                cost = quantity * price
            previous_qty = current["quantity"]
            new_qty = previous_qty + quantity
            current["avg_price"] = ((previous_qty * current["avg_price"]) + cost) / new_qty if new_qty > 0 else 0.0
            current["quantity"] = new_qty
            self.cash -= cost
        elif action == "SELL":
            sell_qty = min(quantity, current["quantity"])
            self.cash += sell_qty * price
            current["quantity"] -= sell_qty
            if current["quantity"] <= 0:
                current["avg_price"] = 0.0
        return self.snapshot()

    def mark_to_market(self, prices: dict[str, float], timestamp) -> dict:
        holdings = 0.0
        unrealized = 0.0
        for symbol, position in self.positions.items():
            price = float(prices.get(symbol, position.get("avg_price", 0.0)))
            quantity = float(position.get("quantity", 0.0))
            holdings += quantity * price
            unrealized += quantity * (price - float(position.get("avg_price", 0.0)))
        equity = self.cash + holdings
        snapshot = {
            "timestamp": pd.Timestamp(timestamp),
            "cash": float(self.cash),
            "holdings": float(holdings),
            "equity": float(equity),
            "unrealized_pnl": float(unrealized),
            "positions": self.positions,
        }
        self.equity_curve.append(snapshot)
        return snapshot

    def snapshot(self) -> dict:
        return {
            "cash": float(self.cash),
            "positions": self.positions,
            "equity": float(self.cash),
        }

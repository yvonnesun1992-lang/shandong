from __future__ import annotations

from datetime import UTC, datetime
from typing import Mapping


class PaperBroker:
    """A strict no-real-money paper broker for simulations."""

    def __init__(self, initial_cash: float = 100_000.0, fee: float = 0.001, slippage: float = 0.0005) -> None:
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        self.fee = float(fee)
        self.slippage = float(slippage)
        self.positions: dict[str, int] = {}
        self.trades: list[dict] = []
        self.portfolio_history: list[dict] = []

    def place_order(self, symbol: str, action: str, price: float, shares: int, timestamp=None) -> dict:
        clean_symbol = symbol.upper().strip()
        clean_action = action.upper().strip()
        clean_shares = int(shares)
        clean_price = float(price)
        if clean_action not in {"BUY", "SELL"} or clean_shares <= 0 or clean_price <= 0:
            return self._rejected(clean_symbol, clean_action, clean_price, clean_shares, "invalid order")

        if clean_action == "BUY":
            exec_price = clean_price * (1 + self.slippage)
            cost = exec_price * clean_shares * (1 + self.fee)
            if cost > self.cash:
                return self._rejected(clean_symbol, clean_action, exec_price, clean_shares, "insufficient cash")
            self.cash -= cost
            self.positions[clean_symbol] = self.positions.get(clean_symbol, 0) + clean_shares
            return self._filled(clean_symbol, clean_action, exec_price, clean_shares, timestamp, cost)

        held = self.positions.get(clean_symbol, 0)
        if clean_shares > held:
            return self._rejected(clean_symbol, clean_action, clean_price, clean_shares, "insufficient position")
        exec_price = clean_price * (1 - self.slippage)
        proceeds = exec_price * clean_shares * (1 - self.fee)
        self.cash += proceeds
        remaining = held - clean_shares
        if remaining:
            self.positions[clean_symbol] = remaining
        else:
            self.positions.pop(clean_symbol, None)
        return self._filled(clean_symbol, clean_action, exec_price, clean_shares, timestamp, proceeds)

    def update_portfolio(self, market_prices: Mapping[str, float] | None = None, timestamp=None) -> dict:
        prices = {key.upper(): float(value) for key, value in (market_prices or {}).items()}
        holdings = {}
        holdings_value = 0.0
        for symbol, shares in sorted(self.positions.items()):
            price = prices.get(symbol, 0.0)
            value = shares * price
            holdings[symbol] = {"shares": shares, "price": price, "value": value}
            holdings_value += value

        snapshot = {
            "timestamp": timestamp or datetime.now(UTC),
            "cash": float(self.cash),
            "holdings": holdings,
            "holdings_value": float(holdings_value),
            "total_equity": float(self.cash + holdings_value),
        }
        self.portfolio_history.append(snapshot)
        return snapshot

    def _filled(self, symbol: str, action: str, price: float, shares: int, timestamp, gross_value: float) -> dict:
        order = {
            "timestamp": timestamp or datetime.now(UTC),
            "symbol": symbol,
            "action": action,
            "price": float(price),
            "shares": int(shares),
            "gross_value": float(gross_value),
            "status": "FILLED",
        }
        self.trades.append(order)
        return order

    @staticmethod
    def _rejected(symbol: str, action: str, price: float, shares: int, reason: str) -> dict:
        return {
            "timestamp": datetime.now(UTC),
            "symbol": symbol,
            "action": action,
            "price": float(price),
            "shares": int(shares),
            "status": "REJECTED",
            "reason": reason,
        }

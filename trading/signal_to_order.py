from __future__ import annotations

from trading.order import Order
from trading.paper_account import PaperAccount


class SignalToOrderConverter:
    def __init__(self, max_order_pct: float = 0.10, max_asset_pct: float = 0.20) -> None:
        self.max_order_pct = float(max_order_pct)
        self.max_asset_pct = float(max_asset_pct)

    def convert(self, signal: dict, account: PaperAccount, market_price: float) -> Order | None:
        action = str(signal.get("action", "HOLD")).upper()
        if action == "HOLD":
            return None
        if action not in {"BUY", "SELL"}:
            return None
        symbol = str(signal["symbol"]).upper()
        strength = max(0.0, min(1.0, float(signal.get("strength", 0.0))))
        equity = account.calculate_equity()
        if action == "BUY":
            max_order_value = equity * self.max_order_pct * strength
            current_value = account.positions.get(symbol, {}).get("quantity", 0.0) * float(market_price)
            remaining_asset_value = max(equity * self.max_asset_pct - current_value, 0.0)
            order_value = min(max_order_value, remaining_asset_value)
            quantity = int(order_value / float(market_price))
        else:
            current_quantity = account.positions.get(symbol, {}).get("quantity", 0.0)
            quantity = int(current_quantity * strength)
        if quantity <= 0:
            return None
        return Order(
            symbol=symbol,
            side=action,
            quantity=quantity,
            order_type="MARKET",
            price=float(market_price),
            timestamp=signal.get("timestamp"),
        )

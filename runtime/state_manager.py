from __future__ import annotations

from trading.paper_account import PaperAccount


class StateManager:
    def __init__(self, account: PaperAccount) -> None:
        self.account = account
        self.active_orders: list[dict] = []
        self.open_trades: list[dict] = []
        self.market_regime = {"state": "unknown", "confidence": 0.0}
        self.current_prices: dict[str, float] = {}

    def update_price(self, symbol: str, price: float) -> dict:
        self.current_prices[str(symbol).upper()] = float(price)
        self.account.update_market_price(str(symbol).upper(), float(price))
        return self.snapshot()

    def add_order(self, order) -> None:
        self.active_orders.append({"order_id": order.order_id, "symbol": order.symbol, "side": order.side, "quantity": order.quantity})

    def add_trade(self, execution) -> None:
        self.open_trades.append(execution.as_dict())
        self.active_orders = [order for order in self.active_orders if order["order_id"] != execution.order_id]

    def snapshot(self) -> dict:
        summary = self.account.summary()
        summary.update(
            {
                "active_orders": list(self.active_orders),
                "open_trades": list(self.open_trades),
                "market_regime": self.market_regime,
            }
        )
        return summary



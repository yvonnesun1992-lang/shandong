from __future__ import annotations

from trading.order import Order
from trading.paper_account import PaperAccount


class RiskLimits:
    def __init__(
        self,
        max_position_per_asset: float = 0.20,
        max_order_value: float = 0.10,
        max_daily_loss: float = 0.03,
        max_drawdown: float = 0.10,
    ) -> None:
        self.max_position_per_asset = float(max_position_per_asset)
        self.max_order_value = float(max_order_value)
        self.max_daily_loss = float(max_daily_loss)
        self.max_drawdown = float(max_drawdown)
        self.peak_equity = 0.0
        self.day_start_equity: float | None = None
        self.stop_new_positions = False

    def update_equity(self, equity: float) -> dict:
        current = float(equity)
        self.peak_equity = max(self.peak_equity, current)
        if self.day_start_equity is None:
            self.day_start_equity = current
        drawdown = (self.peak_equity - current) / self.peak_equity if self.peak_equity > 0 else 0.0
        daily_loss = (self.day_start_equity - current) / self.day_start_equity if self.day_start_equity and self.day_start_equity > 0 else 0.0
        if drawdown > self.max_drawdown or daily_loss > self.max_daily_loss:
            self.stop_new_positions = True
        return {"drawdown": float(drawdown), "daily_loss": float(daily_loss), "stop_new_positions": self.stop_new_positions}

    def validate_order(self, order: Order, account: PaperAccount, market_price: float) -> dict:
        if self.stop_new_positions and order.side == "BUY":
            return {"approved": False, "reason": "RISK_STOP_ACTIVE"}
        equity = account.calculate_equity()
        order_value = float(order.quantity) * float(market_price)
        if order.side == "BUY" and equity > 0 and order_value / equity > self.max_order_value + 1e-12:
            return {"approved": False, "reason": "MAX_ORDER_VALUE"}
        current_position_value = account.positions.get(order.symbol, {}).get("quantity", 0.0) * float(market_price)
        if order.side == "BUY" and equity > 0 and (current_position_value + order_value) / equity > self.max_position_per_asset + 1e-12:
            return {"approved": False, "reason": "MAX_POSITION_PER_ASSET"}
        return {"approved": True, "reason": "OK"}

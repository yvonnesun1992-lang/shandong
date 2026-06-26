from __future__ import annotations

from trading.order import ExecutionResult, Order
from trading.paper_account import PaperAccount


class ExecutionEngine:
    def __init__(self, fee_rate: float = 0.001, slippage_rate: float = 0.0005) -> None:
        self.fee_rate = float(fee_rate)
        self.slippage_rate = float(slippage_rate)

    def execute(self, order: Order, market_price: float, account: PaperAccount) -> ExecutionResult:
        rejection = self._rejection_reason(order, market_price, account)
        if rejection:
            return ExecutionResult(
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                quantity=float(order.quantity),
                status="REJECTED",
                reason=rejection,
                market_price=float(market_price or 0.0),
                timestamp=order.timestamp,
            )
        if order.side == "BUY":
            execution_price = float(market_price) * (1 + self.slippage_rate)
            gross = execution_price * float(order.quantity)
            fee = gross * self.fee_rate
            cash_effect = -(gross + fee)
            slippage_cost = (execution_price - float(market_price)) * float(order.quantity)
        else:
            execution_price = float(market_price) * (1 - self.slippage_rate)
            gross = execution_price * float(order.quantity)
            fee = gross * self.fee_rate
            cash_effect = gross - fee
            slippage_cost = (float(market_price) - execution_price) * float(order.quantity)
        return ExecutionResult(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=float(order.quantity),
            status="FILLED",
            market_price=float(market_price),
            execution_price=float(execution_price),
            fee=float(fee),
            slippage_cost=float(slippage_cost),
            cash_effect=float(cash_effect),
            timestamp=order.timestamp,
        )

    def _rejection_reason(self, order: Order, market_price: float, account: PaperAccount) -> str:
        if float(order.quantity) <= 0:
            return "INVALID_QUANTITY"
        if float(market_price or 0.0) <= 0:
            return "INVALID_PRICE"
        if order.side not in {"BUY", "SELL"}:
            return "INVALID_SIDE"
        if order.order_type not in {"MARKET", "LIMIT"}:
            return "INVALID_ORDER_TYPE"
        if order.side == "BUY":
            execution_price = float(market_price) * (1 + self.slippage_rate)
            gross = execution_price * float(order.quantity)
            total_cost = gross * (1 + self.fee_rate)
            if not account.can_buy(total_cost):
                return "INSUFFICIENT_CASH"
        if order.side == "SELL" and not account.can_sell(order.symbol, order.quantity):
            return "INSUFFICIENT_POSITION"
        return ""

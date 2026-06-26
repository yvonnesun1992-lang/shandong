from __future__ import annotations

from trading.execution_engine import ExecutionEngine
from trading.order import ExecutionResult, Order
from trading.paper_account import PaperAccount


class PaperBroker:
    def __init__(self, initial_cash: float = 100_000.0, fee_rate: float = 0.001, slippage_rate: float = 0.0005) -> None:
        self.account = PaperAccount(initial_cash=initial_cash)
        self.execution_engine = ExecutionEngine(fee_rate=fee_rate, slippage_rate=slippage_rate)
        self.order_history: list[dict] = []

    def submit_order(self, order: Order) -> Order:
        self.order_history.append({"order_id": order.order_id, "symbol": order.symbol, "side": order.side, "status": order.status})
        return order

    def execute_order(self, order: Order, market_price: float) -> ExecutionResult:
        self.submit_order(order)
        result = self.execution_engine.execute(order, market_price=market_price, account=self.account)
        if result.status == "FILLED":
            self.account.apply_execution(result)
        return result

    def get_account_summary(self) -> dict:
        return self.account.summary()

    def get_positions(self) -> dict:
        return self.account.positions

    def get_trade_history(self) -> list[dict]:
        return list(self.account.trade_history)

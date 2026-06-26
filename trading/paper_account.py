from __future__ import annotations

from trading.order import ExecutionResult


class PaperAccount:
    def __init__(self, initial_cash: float = 100_000.0) -> None:
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        self.positions: dict[str, dict] = {}
        self.market_prices: dict[str, float] = {}
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.trade_history: list[dict] = []

    @property
    def equity(self) -> float:
        return self.calculate_equity()

    def can_buy(self, cost: float) -> bool:
        return float(cost) <= self.cash + 1e-9

    def can_sell(self, symbol: str, quantity: float) -> bool:
        return self.positions.get(symbol, {}).get("quantity", 0.0) + 1e-9 >= float(quantity)

    def apply_execution(self, execution: ExecutionResult) -> None:
        if execution.status != "FILLED":
            return
        if execution.side == "BUY":
            self.buy(execution.symbol, execution.quantity, execution.execution_price, execution.fee)
        elif execution.side == "SELL":
            self.sell(execution.symbol, execution.quantity, execution.execution_price, execution.fee)
        self.trade_history.append(execution.as_dict())
        self.update_market_price(execution.symbol, execution.execution_price)

    def buy(self, symbol: str, quantity: float, price: float, fee: float = 0.0) -> None:
        cost = float(quantity) * float(price) + float(fee)
        if cost > self.cash + 1e-9:
            raise ValueError("cash cannot become negative")
        position = self.positions.setdefault(symbol, {"quantity": 0.0, "avg_price": 0.0})
        previous_quantity = position["quantity"]
        new_quantity = previous_quantity + float(quantity)
        total_cost_basis = previous_quantity * position["avg_price"] + float(quantity) * float(price)
        position["quantity"] = new_quantity
        position["avg_price"] = total_cost_basis / new_quantity if new_quantity > 0 else 0.0
        self.cash -= cost

    def sell(self, symbol: str, quantity: float, price: float, fee: float = 0.0) -> None:
        position = self.positions.get(symbol)
        if position is None or position["quantity"] + 1e-9 < float(quantity):
            raise ValueError("position cannot become negative")
        sell_quantity = float(quantity)
        proceeds = sell_quantity * float(price) - float(fee)
        self.cash += proceeds
        self.realized_pnl += sell_quantity * (float(price) - position["avg_price"]) - float(fee)
        position["quantity"] -= sell_quantity
        if position["quantity"] <= 1e-9:
            self.positions.pop(symbol, None)

    def update_market_price(self, symbol: str, price: float) -> None:
        self.market_prices[str(symbol).upper()] = float(price)
        self.calculate_pnl()

    def calculate_position_value(self) -> float:
        total = 0.0
        for symbol, position in self.positions.items():
            price = self.market_prices.get(symbol, position["avg_price"])
            total += position["quantity"] * price
        return float(total)

    def calculate_equity(self) -> float:
        return float(self.cash + self.calculate_position_value())

    def calculate_pnl(self) -> dict:
        unrealized = 0.0
        for symbol, position in self.positions.items():
            price = self.market_prices.get(symbol, position["avg_price"])
            unrealized += position["quantity"] * (price - position["avg_price"])
        self.unrealized_pnl = float(unrealized)
        return {"realized_pnl": self.realized_pnl, "unrealized_pnl": self.unrealized_pnl}

    def summary(self) -> dict:
        self.calculate_pnl()
        position_value = self.calculate_position_value()
        return {
            "initial_cash": self.initial_cash,
            "cash": float(self.cash),
            "position_value": position_value,
            "equity": float(self.cash + position_value),
            "realized_pnl": float(self.realized_pnl),
            "unrealized_pnl": float(self.unrealized_pnl),
            "positions": self.positions,
        }

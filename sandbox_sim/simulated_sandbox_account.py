from __future__ import annotations

from dataclasses import dataclass, field

from sandbox_sim.simulated_sandbox_order import SimulatedSandboxFill


@dataclass
class SimulatedSandboxAccount:
    initial_cash: float = 100000.0
    cash: float | None = None
    positions: dict[str, int] = field(default_factory=dict)
    market_prices: dict[str, float] = field(default_factory=dict)
    realized_pnl: float = 0.0

    def __post_init__(self) -> None:
        if self.cash is None:
            self.cash = float(self.initial_cash)

    def update_market_price(self, symbol: str, price: float) -> None:
        if price > 0:
            self.market_prices[symbol.upper()] = float(price)

    def apply_fill(self, fill: SimulatedSandboxFill) -> None:
        symbol = fill.symbol.upper()
        quantity = int(fill.quantity)
        value = fill.fill_price * quantity
        if fill.side == "BUY":
            self.cash = float(self.cash or 0.0) - value - fill.commission
            self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        elif fill.side == "SELL":
            current = self.positions.get(symbol, 0)
            sell_quantity = min(quantity, current)
            self.cash = float(self.cash or 0.0) + fill.fill_price * sell_quantity - fill.commission
            remaining = current - sell_quantity
            if remaining:
                self.positions[symbol] = remaining
            else:
                self.positions.pop(symbol, None)
            self.realized_pnl += fill.fill_price * sell_quantity - fill.commission
        self.update_market_price(symbol, fill.fill_price)

    def calculate_position_value(self) -> float:
        return sum(quantity * self.market_prices.get(symbol, 0.0) for symbol, quantity in self.positions.items())

    def calculate_unrealized_pnl(self) -> float:
        return self.calculate_position_value() - sum(0.0 for _ in self.positions)

    def calculate_equity(self) -> float:
        return float(self.cash or 0.0) + self.calculate_position_value()

    def get_account_snapshot(self) -> dict:
        equity = self.calculate_equity()
        return {
            "cash": round(float(self.cash or 0.0), 6),
            "equity": round(equity, 6),
            "buying_power": round(max(float(self.cash or 0.0), 0.0), 6),
            "positions": dict(self.positions),
            "realized_pnl": round(self.realized_pnl, 6),
            "unrealized_pnl": round(self.calculate_unrealized_pnl(), 6),
            "simulation_only": True,
            "broker_connected": False,
            "real_money_enabled": False,
            "paper_trading": True,
        }

    def get_positions_snapshot(self) -> list[dict]:
        return [
            {
                "symbol": symbol,
                "quantity": quantity,
                "market_price": self.market_prices.get(symbol, 0.0),
                "market_value": round(quantity * self.market_prices.get(symbol, 0.0), 6),
                "simulation_only": True,
            }
            for symbol, quantity in sorted(self.positions.items())
        ]

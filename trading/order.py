from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from itertools import count


_ORDER_COUNTER = count(1)


@dataclass(frozen=True)
class Order:
    symbol: str
    side: str
    quantity: float
    order_type: str = "MARKET"
    price: float | None = None
    timestamp: datetime | str | None = None
    status: str = "NEW"
    reason: str = ""
    order_id: str = field(default_factory=lambda: f"PAPER-{next(_ORDER_COUNTER):08d}")

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol", str(self.symbol).upper())
        object.__setattr__(self, "side", str(self.side).upper())
        object.__setattr__(self, "order_type", str(self.order_type).upper())
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now(UTC).replace(microsecond=0))

    def with_status(self, status: str, reason: str = "") -> "Order":
        return replace(self, status=str(status).upper(), reason=str(reason or ""))


@dataclass(frozen=True)
class ExecutionResult:
    order_id: str
    symbol: str
    side: str
    quantity: float
    status: str
    reason: str = ""
    market_price: float = 0.0
    execution_price: float = 0.0
    fee: float = 0.0
    slippage_cost: float = 0.0
    cash_effect: float = 0.0
    timestamp: datetime | str | None = None

    def as_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "status": self.status,
            "reason": self.reason,
            "market_price": self.market_price,
            "execution_price": self.execution_price,
            "fee": self.fee,
            "slippage_cost": self.slippage_cost,
            "cash_effect": self.cash_effect,
            "timestamp": self.timestamp,
        }

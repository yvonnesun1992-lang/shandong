from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from itertools import count


_ORDER_COUNTER = count(1)
_FILL_COUNTER = count(1)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass
class SimulatedSandboxOrder:
    sandbox_order_id: str
    symbol: str
    side: str
    quantity: int
    order_type: str = "MARKET"
    limit_price: float | None = None
    status: str = "NEW"
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    reason: str = ""
    simulation_only: bool = True
    real_order_submitted: bool = False
    broker_connected: bool = False
    real_money_enabled: bool = False

    @classmethod
    def create(
        cls,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str = "MARKET",
        limit_price: float | None = None,
        reason: str = "",
    ) -> "SimulatedSandboxOrder":
        return cls(
            sandbox_order_id=f"SIM-{next(_ORDER_COUNTER):08d}",
            symbol=symbol.upper(),
            side=side.upper(),
            quantity=int(quantity),
            order_type=order_type.upper(),
            limit_price=limit_price,
            reason=reason,
        )

    def set_status(self, status: str, reason: str = "") -> None:
        self.status = status
        self.reason = reason
        self.updated_at = _now()

    def to_dict(self) -> dict:
        return {
            "sandbox_order_id": self.sandbox_order_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "order_type": self.order_type,
            "limit_price": self.limit_price,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "reason": self.reason,
            "simulation_only": self.simulation_only,
            "real_order_submitted": self.real_order_submitted,
            "broker_connected": self.broker_connected,
            "real_money_enabled": self.real_money_enabled,
        }


@dataclass
class SimulatedSandboxFill:
    fill_id: str
    sandbox_order_id: str
    symbol: str
    side: str
    quantity: int
    fill_price: float
    fill_time: str = field(default_factory=_now)
    commission: float = 0.0
    simulation_only: bool = True

    @classmethod
    def create(
        cls,
        sandbox_order_id: str,
        symbol: str,
        side: str,
        quantity: int,
        fill_price: float,
        commission: float = 0.0,
    ) -> "SimulatedSandboxFill":
        return cls(
            fill_id=f"FILL-{next(_FILL_COUNTER):08d}",
            sandbox_order_id=sandbox_order_id,
            symbol=symbol.upper(),
            side=side.upper(),
            quantity=int(quantity),
            fill_price=float(fill_price),
            commission=float(commission),
        )

    def to_dict(self) -> dict:
        return {
            "fill_id": self.fill_id,
            "sandbox_order_id": self.sandbox_order_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "fill_price": self.fill_price,
            "fill_time": self.fill_time,
            "commission": self.commission,
            "simulation_only": self.simulation_only,
        }

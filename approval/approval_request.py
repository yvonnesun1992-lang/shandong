from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


APPROVAL_STATES = {"DRAFT", "PENDING_REVIEW", "APPROVED_SIMULATED", "REJECTED", "EXPIRED"}


@dataclass
class ApprovalRequest:
    approval_id: str
    order_intent_id: str
    symbol: str
    side: str
    quantity: float
    order_type: str
    notional_value: float
    signal_source: str
    signal_strength: float
    risk_summary: dict[str, Any]
    status: str = "DRAFT"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    reviewed_at: str | None = None
    reviewer: str | None = None
    reason: str = "manual approval planning only"

    @classmethod
    def create(
        cls,
        order_intent_id: str,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str,
        notional_value: float,
        signal_source: str,
        signal_strength: float,
        risk_summary: dict[str, Any] | None = None,
        status: str = "DRAFT",
    ) -> "ApprovalRequest":
        safe_status = status if status in APPROVAL_STATES else "DRAFT"
        return cls(
            approval_id=f"approval-{uuid4().hex[:12]}",
            order_intent_id=str(order_intent_id),
            symbol=str(symbol).upper(),
            side=str(side).upper(),
            quantity=float(quantity),
            order_type=str(order_type).upper(),
            notional_value=float(notional_value),
            signal_source=str(signal_source),
            signal_strength=max(0.0, min(1.0, float(signal_strength))),
            risk_summary=dict(risk_summary or {}),
            status=safe_status,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "order_intent_id": self.order_intent_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "order_type": self.order_type,
            "notional_value": self.notional_value,
            "signal_source": self.signal_source,
            "signal_strength": self.signal_strength,
            "risk_summary": self.risk_summary,
            "status": self.status,
            "created_at": self.created_at,
            "reviewed_at": self.reviewed_at,
            "reviewer": self.reviewer,
            "reason": self.reason,
            "manual_approval_required": True,
            "auto_approval_enabled": False,
            "real_order_after_approval": False,
            "real_orders_enabled": False,
            "paper_trading": True,
        }

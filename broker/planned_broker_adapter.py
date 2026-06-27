from __future__ import annotations

from typing import Any


PLANNED_REASON = "broker integration planned only"


class PlannedBrokerAdapter:
    def __init__(self, provider: str = "none") -> None:
        self.provider = provider

    def get_account(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "status": "planned_only",
            "broker_connected": False,
            "real_order_submitted": False,
            "paper_trading": True,
            "real_money_enabled": False,
            "reason": PLANNED_REASON,
        }

    def get_positions(self) -> list[dict[str, Any]]:
        return []

    def submit_order(self, order: dict[str, Any]) -> dict[str, Any]:
        return self._planned_response("rejected", "submit", order_ref=_safe_order_ref(order))

    def cancel_order(self, order_id: str) -> dict[str, Any]:
        return self._planned_response("planned_only", "cancel", order_ref=str(order_id))

    def get_order_status(self, order_id: str) -> dict[str, Any]:
        return self._planned_response("planned_only", "status", order_ref=str(order_id))

    def _planned_response(self, status: str, action: str, order_ref: str) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "action": action,
            "order_ref": order_ref,
            "status": status,
            "broker_connected": False,
            "real_order_submitted": False,
            "paper_trading": True,
            "real_money_enabled": False,
            "reason": PLANNED_REASON,
        }


def _safe_order_ref(order: dict[str, Any]) -> str:
    symbol = str(order.get("symbol", "UNKNOWN")).upper()
    side = str(order.get("side", order.get("action", "UNKNOWN"))).upper()
    return f"{symbol}:{side}:planned"

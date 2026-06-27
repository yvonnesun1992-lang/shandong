from __future__ import annotations

from typing import Any


class BrokerAdapterInterface:
    """Planning-only broker adapter contract.

    This interface documents future adapter shape. It intentionally does not
    connect to any external service or submit real orders.
    """

    def get_account(self) -> dict[str, Any]:
        raise NotImplementedError("broker adapter planned only; no external broker connection")

    def get_positions(self) -> list[dict[str, Any]]:
        raise NotImplementedError("broker adapter planned only; no external broker positions")

    def submit_order(self, order: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("broker adapter planned only; no external broker order submission")

    def cancel_order(self, order_id: str) -> dict[str, Any]:
        raise NotImplementedError("broker adapter planned only; no external broker order cancellation")

    def get_order_status(self, order_id: str) -> dict[str, Any]:
        raise NotImplementedError("broker adapter planned only; no external broker order status")

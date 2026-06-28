from __future__ import annotations

from broker_adapter.base_adapter import BrokerAdapterBase


class SkeletonBrokerAdapter(BrokerAdapterBase):
    adapter_name = "skeleton"

    def __init__(self, config: dict | None = None) -> None:
        self.config = config or {}

    def connect(self) -> dict:
        return self._payload("connect", status="skeleton_only", reason="V5.15 skeleton only stage")

    def disconnect(self) -> dict:
        return self._payload("disconnect", status="skeleton_only")

    def is_connected(self) -> bool:
        return False

    def get_account(self) -> dict:
        return {**self._payload("get_account", status="skeleton_only"), "account": {}}

    def get_positions(self) -> dict:
        return {**self._payload("get_positions", status="skeleton_only"), "positions": []}

    def submit_order(self, order: dict) -> dict:
        return {**self._payload("submit_order", status="skeleton_only_rejected"), "order": {}, "reason": "skeleton adapter rejects orders"}

    def cancel_order(self, order_id: str) -> dict:
        return {**self._payload("cancel_order", status="skeleton_only_rejected"), "order_id": str(order_id)}

    def get_order_status(self, order_id: str) -> dict:
        return {**self._payload("get_order_status", status="skeleton_only"), "order_id": str(order_id), "order_status": "not_implemented"}

    def get_recent_orders(self) -> dict:
        return {**self._payload("get_recent_orders", status="skeleton_only"), "orders": []}

    def health_check(self) -> dict:
        return {**self._payload("health_check", status="skeleton_only"), "health": "not_implemented"}

    def _payload(self, method: str, status: str, reason: str = "not implemented") -> dict:
        return {
            "adapter": self.adapter_name,
            "method": method,
            "status": status,
            "reason": reason,
            "skeleton_only": True,
            "real_connection": False,
            "real_orders": False,
            "paper_trading": True,
        }


class FutuSkeletonAdapter(SkeletonBrokerAdapter):
    adapter_name = "futu_skeleton"


class TigerSkeletonAdapter(SkeletonBrokerAdapter):
    adapter_name = "tiger_skeleton"


class SchwabSkeletonAdapter(SkeletonBrokerAdapter):
    adapter_name = "schwab_skeleton"

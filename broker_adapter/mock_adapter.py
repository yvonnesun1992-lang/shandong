from __future__ import annotations

from broker_adapter.base_adapter import BrokerAdapterBase
from sandbox_connector.mock_sandbox_connector import MockSandboxConnector


class MockBrokerAdapter(BrokerAdapterBase):
    adapter_name = "mock"

    def __init__(self, config: dict | None = None) -> None:
        self.config = config or {}
        self.connector = MockSandboxConnector()

    def connect(self) -> dict:
        return self._boundary("connect", status="mock_connected")

    def disconnect(self) -> dict:
        return self._boundary("disconnect", status="mock_disconnected")

    def is_connected(self) -> bool:
        return True

    def get_account(self) -> dict:
        return {**self.connector.get_account(), **self._boundary("get_account")}

    def get_positions(self) -> dict:
        return {**self.connector.get_positions(), **self._boundary("get_positions")}

    def submit_order(self, order: dict) -> dict:
        return {**self.connector.submit_order(order), **self._boundary("submit_order")}

    def cancel_order(self, order_id: str) -> dict:
        return {**self.connector.cancel_order({"client_order_id": str(order_id)}), **self._boundary("cancel_order")}

    def get_order_status(self, order_id: str) -> dict:
        return {**self.connector.get_order_status({"client_order_id": str(order_id)}), **self._boundary("get_order_status")}

    def get_recent_orders(self) -> dict:
        return {**self.connector.get_recent_orders(), **self._boundary("get_recent_orders")}

    def health_check(self) -> dict:
        return {**self.connector.health_check(), **self._boundary("health_check")}

    def _boundary(self, method: str, status: str = "mock_only") -> dict:
        return {
            "adapter": "mock",
            "method": method,
            "status": status,
            "skeleton_only": False,
            "mock_only": True,
            "real_connection": False,
            "real_orders": False,
            "paper_trading": True,
        }

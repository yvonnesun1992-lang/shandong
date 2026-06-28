from __future__ import annotations


class BrokerAdapterBase:
    adapter_name = "base"

    def connect(self) -> dict:
        raise NotImplementedError("broker adapter connect is not implemented")

    def disconnect(self) -> dict:
        raise NotImplementedError("broker adapter disconnect is not implemented")

    def is_connected(self) -> bool:
        raise NotImplementedError("broker adapter connection state is not implemented")

    def get_account(self) -> dict:
        raise NotImplementedError("broker adapter account access is not implemented")

    def get_positions(self) -> dict:
        raise NotImplementedError("broker adapter position access is not implemented")

    def submit_order(self, order: dict) -> dict:
        raise NotImplementedError("broker adapter order submission is not implemented")

    def cancel_order(self, order_id: str) -> dict:
        raise NotImplementedError("broker adapter cancel is not implemented")

    def get_order_status(self, order_id: str) -> dict:
        raise NotImplementedError("broker adapter order status is not implemented")

    def get_recent_orders(self) -> dict:
        raise NotImplementedError("broker adapter recent orders is not implemented")

    def health_check(self) -> dict:
        raise NotImplementedError("broker adapter health check is not implemented")

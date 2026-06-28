from __future__ import annotations

from broker_adapter.alpaca_skeleton_adapter import AlpacaSkeletonAdapter
from broker_adapter.base_adapter import BrokerAdapterBase
from broker_adapter.ibkr_skeleton_adapter import IBKRSkeletonAdapter
from broker_adapter.mock_adapter import MockBrokerAdapter
from broker_adapter.skeleton_adapters import FutuSkeletonAdapter, SchwabSkeletonAdapter, TigerSkeletonAdapter


class BrokerAdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, type[BrokerAdapterBase]] = {}

    def register_adapter(self, name: str, adapter_class: type[BrokerAdapterBase]) -> None:
        self._adapters[str(name)] = adapter_class

    def get_adapter(self, name: str) -> type[BrokerAdapterBase] | None:
        return self._adapters.get(str(name))

    def list_adapters(self) -> list[str]:
        return sorted(self._adapters)

    def create_adapter(self, name: str, config: dict | None = None) -> BrokerAdapterBase:
        adapter_class = self.get_adapter(name)
        if adapter_class is None:
            raise ValueError(f"unknown broker adapter: {name}")
        return adapter_class(config=config)

    def as_dict(self) -> dict:
        return {
            "version": "V5.15",
            "adapters": self.list_adapters(),
            "skeleton_only": True,
            "real_connection": False,
            "paper_trading": True,
        }


def build_default_registry() -> BrokerAdapterRegistry:
    registry = BrokerAdapterRegistry()
    registry.register_adapter("mock", MockBrokerAdapter)
    registry.register_adapter("ibkr_skeleton", IBKRSkeletonAdapter)
    registry.register_adapter("alpaca_skeleton", AlpacaSkeletonAdapter)
    registry.register_adapter("futu_skeleton", FutuSkeletonAdapter)
    registry.register_adapter("tiger_skeleton", TigerSkeletonAdapter)
    registry.register_adapter("schwab_skeleton", SchwabSkeletonAdapter)
    return registry

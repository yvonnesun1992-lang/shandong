from __future__ import annotations

from broker_adapter.adapter_registry import build_default_registry
from broker_adapter.base_adapter import BrokerAdapterBase
from broker_adapter.safety_guard import validate_adapter_safety


def create_broker_adapter(provider_name: str = "mock", mode: str = "skeleton_only", config: dict | None = None) -> BrokerAdapterBase:
    provider = str(provider_name or "mock")
    validation = validate_adapter_safety(provider, config or {})
    if not validation["safe"]:
        raise ValueError("unsafe broker adapter configuration")
    registry = build_default_registry()
    adapter = registry.create_adapter(provider, config={**(config or {}), "mode": mode})
    return adapter


def build_factory_status(provider_name: str = "ibkr_skeleton") -> dict:
    adapter = create_broker_adapter(provider_name)
    return {
        "version": "V5.15",
        "provider": provider_name,
        "adapter": adapter.connect(),
        "skeleton_only": provider_name != "mock",
        "real_connection": False,
        "paper_trading": True,
    }

from __future__ import annotations

from sandbox_connector.connector_interface_contract import CONNECTOR_METHODS

from broker_adapter.adapter_registry import build_default_registry


def validate_interface_compatibility() -> dict:
    missing = detect_missing_methods()
    return {
        "compatible": not missing["missing_methods"],
        "missing_methods": missing["missing_methods"],
        "mock_only": True,
        "skeleton_only": True,
        "real_connection": False,
        "paper_trading": True,
    }


def map_mock_to_skeleton_schema() -> dict:
    return {
        "version": "V5.15",
        "mapping": {
            "get_account": "get_account",
            "get_positions": "get_positions",
            "submit_order": "submit_order",
            "cancel_order": "cancel_order",
            "get_order_status": "get_order_status",
            "get_recent_orders": "get_recent_orders",
            "health_check": "health_check",
        },
        "mock_only": True,
        "skeleton_only": True,
        "real_connection": False,
        "paper_trading": True,
    }


def detect_missing_methods() -> dict:
    registry = build_default_registry()
    missing = []
    for adapter_name in registry.list_adapters():
        adapter = registry.create_adapter(adapter_name)
        for method in CONNECTOR_METHODS:
            if not hasattr(adapter, method):
                missing.append({"adapter": adapter_name, "method": method})
    return {"missing_methods": missing, "real_connection": False, "paper_trading": True}


def validate_contract_alignment() -> dict:
    compatibility = validate_interface_compatibility()
    return {
        "aligned": compatibility["compatible"],
        "compatibility": compatibility,
        "mock_connector": "V5.14",
        "adapter_skeleton": "V5.15",
        "real_connection": False,
        "paper_trading": True,
    }

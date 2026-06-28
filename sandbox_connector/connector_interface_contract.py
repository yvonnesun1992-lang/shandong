from __future__ import annotations


CONNECTOR_METHODS = ["get_account", "get_positions", "submit_order", "cancel_order", "get_order_status", "get_recent_orders", "health_check"]


class ConnectorInterfaceContract:
    contract_only = True
    connector_runtime_enabled = False

    def get_account(self) -> dict:
        return _fallback("get_account")

    def get_positions(self) -> dict:
        return _fallback("get_positions", positions=[])

    def submit_order(self, request: dict) -> dict:
        return _fallback("submit_order", error_code="CONNECTOR_DISABLED")

    def cancel_order(self, request: dict) -> dict:
        return _fallback("cancel_order", error_code="CONNECTOR_DISABLED")

    def get_order_status(self, request: dict) -> dict:
        return _fallback("get_order_status", error_code="CONNECTOR_DISABLED")

    def get_recent_orders(self) -> dict:
        return _fallback("get_recent_orders", orders=[])

    def health_check(self) -> dict:
        return _fallback("health_check", status="contract_only")


def build_interface_contract() -> dict:
    return {
        "methods": CONNECTOR_METHODS,
        "contract_only": True,
        "connector_runtime_enabled": False,
        "real_sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def _fallback(method: str, **extra: object) -> dict:
    return {
        "method": method,
        "contract_only": True,
        "connector_runtime_enabled": False,
        "real_sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        **extra,
    }

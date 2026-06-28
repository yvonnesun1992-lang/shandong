from __future__ import annotations

import os


VALID_MOCK_MODES = {"disabled", "mock_enabled"}
VALID_MOCK_PROVIDERS = {"mock"}


def get_mock_connector_mode() -> str:
    value = os.getenv("SHANDONG_V5_MOCK_CONNECTOR_MODE", "mock_enabled").strip().lower()
    return value if value in VALID_MOCK_MODES else "mock_enabled"


def get_mock_connector_provider() -> str:
    value = os.getenv("SHANDONG_V5_MOCK_CONNECTOR_PROVIDER", "mock").strip().lower()
    return value if value in VALID_MOCK_PROVIDERS else "mock"


def get_mock_connector_status() -> dict:
    mode = get_mock_connector_mode()
    return {
        "version": "V5.14",
        "mock_connector_mode": mode,
        "mock_connector_provider": get_mock_connector_provider(),
        "mock_connector_enabled": mode == "mock_enabled",
        "real_connector_runtime_enabled": False,
        "real_sandbox_api_enabled": False,
        "real_broker_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "mock_only": True,
        "warnings": [],
    }

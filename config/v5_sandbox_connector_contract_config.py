from __future__ import annotations

import os


VALID_MODES = {"disabled", "planned", "contract_only"}
VALID_PROVIDERS = {
    "none",
    "alpaca_sandbox_contract",
    "ibkr_paper_contract",
    "futu_sim_contract",
    "tiger_sim_contract",
    "schwab_sandbox_contract",
}


def get_connector_contract_mode() -> str:
    value = os.getenv("SHANDONG_V5_CONNECTOR_CONTRACT_MODE", "contract_only").strip().lower()
    return value if value in VALID_MODES else "contract_only"


def get_connector_contract_provider() -> str:
    value = os.getenv("SHANDONG_V5_CONNECTOR_PROVIDER", "none").strip().lower()
    return value if value in VALID_PROVIDERS else "none"


def get_connector_contract_status() -> dict:
    mode = get_connector_contract_mode()
    return {
        "version": "V5.13",
        "connector_contract_mode": mode,
        "connector_provider": get_connector_contract_provider(),
        "contract_only": mode == "contract_only",
        "connector_runtime_enabled": False,
        "real_sandbox_api_enabled": False,
        "real_broker_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "simulation_only": True,
    }

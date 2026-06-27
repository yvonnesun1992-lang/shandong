from __future__ import annotations

import os


VALID_MODES = {"disabled", "planned", "paper_bridge_planned"}
VALID_PROVIDERS = {"none", "alpaca_planned", "ibkr_planned", "futu_planned", "tiger_planned", "schwab_planned"}
VALID_EXECUTION_MODES = {"paper_only", "manual_approval_planned", "live_planned"}


def get_broker_integration_mode() -> str:
    return _choice(os.getenv("SHANDONG_V5_BROKER_INTEGRATION_MODE"), VALID_MODES, "disabled")


def get_broker_provider_plan() -> str:
    return _choice(os.getenv("SHANDONG_V5_BROKER_PROVIDER"), VALID_PROVIDERS, "none")


def get_broker_execution_mode() -> str:
    requested = _choice(os.getenv("SHANDONG_V5_BROKER_EXECUTION_MODE"), VALID_EXECUTION_MODES, "paper_only")
    if _env_flag("SHANDONG_V5_ENABLE_REAL_ORDERS") or _env_flag("SHANDONG_V5_ENABLE_REAL_MONEY"):
        return "paper_only"
    return requested if requested != "live_planned" else "paper_only"


def get_broker_integration_status() -> dict:
    return {
        "version": "V5.8",
        "broker_integration_mode": get_broker_integration_mode(),
        "broker_provider": get_broker_provider_plan(),
        "broker_execution_mode": get_broker_execution_mode(),
        "enable_broker": False,
        "enable_real_orders": False,
        "enable_real_money": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "warning": [
            "broker integration planning only",
            "real broker connectivity disabled",
            "real order submission disabled",
        ],
    }


def _choice(value: str | None, allowed: set[str], default: str) -> str:
    if not value:
        return default
    normalized = value.strip().lower()
    return normalized if normalized in allowed else default


def _env_flag(name: str) -> bool:
    return str(os.getenv(name, "false")).strip().lower() in {"1", "true", "yes", "on"}

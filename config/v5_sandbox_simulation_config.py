from __future__ import annotations

import os


VALID_SIMULATION_MODES = {"disabled", "local_simulation", "stress_simulation"}


def get_sandbox_simulation_mode() -> str:
    value = os.getenv("SHANDONG_V5_SANDBOX_SIMULATION_MODE", "local_simulation").strip().lower()
    return value if value in VALID_SIMULATION_MODES else "local_simulation"


def get_sandbox_simulation_policy() -> dict:
    mode = get_sandbox_simulation_mode()
    enabled = _env_bool("SHANDONG_V5_ENABLE_LOCAL_SANDBOX_SIM", True) and mode != "disabled"
    return {
        "sandbox_simulation_mode": mode,
        "local_simulation": enabled,
        "local_sandbox_simulation_enabled": enabled,
        "real_sandbox_api_enabled": False,
        "real_broker_enabled": False,
        "real_money_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "paper_trading": True,
        "simulation_only": True,
        "warnings": [] if enabled else ["local sandbox simulation disabled"],
    }


def get_sandbox_simulation_status() -> dict:
    policy = get_sandbox_simulation_policy()
    return {
        "version": "V5.11",
        **policy,
        "supported_scenarios": [
            "full_fill",
            "partial_fill",
            "reject",
            "cancel",
            "latency",
            "disconnect",
            "insufficient_cash",
            "invalid_symbol",
            "risk_rejected",
        ],
    }


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

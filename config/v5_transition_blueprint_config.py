from __future__ import annotations

import os


VALID_BLUEPRINT_MODES = {"disabled", "blueprint_only", "readiness_review"}
VALID_TARGET_PROVIDERS = {"none", "ibkr", "alpaca", "futu", "tiger", "schwab"}


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_transition_blueprint_mode() -> str:
    value = os.getenv("SHANDONG_V5_TRANSITION_BLUEPRINT_MODE", "blueprint_only").strip().lower()
    return value if value in VALID_BLUEPRINT_MODES else "blueprint_only"


def get_transition_target_provider() -> str:
    value = os.getenv("SHANDONG_V5_TRANSITION_TARGET_PROVIDER", "none").strip().lower()
    return value if value in VALID_TARGET_PROVIDERS else "none"


def get_transition_status() -> dict:
    mode = get_transition_blueprint_mode()
    return {
        "version": "V5.18",
        "transition_blueprint_mode": mode,
        "transition_target_provider": get_transition_target_provider(),
        "blueprint_only": mode in {"blueprint_only", "readiness_review"},
        "transition_enabled": _env_bool("SHANDONG_V5_ENABLE_REAL_BROKER_TRANSITION", False),
        "sandbox_api_enabled": _env_bool("SHANDONG_V5_ENABLE_SANDBOX_API", False),
        "broker_connected": False,
        "real_orders_enabled": _env_bool("SHANDONG_V5_ENABLE_REAL_ORDERS", False),
        "real_money_enabled": _env_bool("SHANDONG_V5_ENABLE_REAL_MONEY", False),
        "paper_trading": True,
        "warnings": [],
    }

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
    warnings = _blocked_real_path_warnings()
    return {
        "version": "V5.18",
        "transition_blueprint_mode": mode,
        "transition_target_provider": get_transition_target_provider(),
        "blueprint_only": True,
        "transition_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": warnings,
    }


def _blocked_real_path_warnings() -> list[str]:
    checks = [
        ("SHANDONG_V5_ENABLE_REAL_BROKER_TRANSITION", "real broker transition requested but blocked in V5.18"),
        ("SHANDONG_V5_ENABLE_SANDBOX_API", "sandbox api requested but blocked in V5.18"),
        ("SHANDONG_V5_ENABLE_REAL_ORDERS", "real orders requested but blocked in V5.18"),
        ("SHANDONG_V5_ENABLE_REAL_MONEY", "real money requested but blocked in V5.18"),
    ]
    return [message for env_name, message in checks if _env_bool(env_name, False)]

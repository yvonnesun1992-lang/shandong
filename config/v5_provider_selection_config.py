from __future__ import annotations

import os


VALID_SELECTION_MODES = {"disabled", "selection_only", "readiness_review"}
DEFAULT_PROVIDERS = ["alpaca", "ibkr", "futu", "tiger", "schwab"]
VALID_PROVIDERS = set(DEFAULT_PROVIDERS)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_provider_selection_mode() -> str:
    value = os.getenv("SHANDONG_V5_PROVIDER_SELECTION_MODE", "selection_only").strip().lower()
    return value if value in VALID_SELECTION_MODES else "selection_only"


def get_candidate_providers() -> list[str]:
    raw = os.getenv("SHANDONG_V5_CANDIDATE_PROVIDERS", ",".join(DEFAULT_PROVIDERS))
    providers = [item.strip().lower() for item in raw.split(",") if item.strip()]
    filtered = [provider for provider in providers if provider in VALID_PROVIDERS]
    return filtered or DEFAULT_PROVIDERS.copy()


def get_provider_selection_status() -> dict:
    return {
        "version": "V5.19",
        "provider_selection_mode": get_provider_selection_mode(),
        "candidate_providers": get_candidate_providers(),
        "selection_only": True,
        "provider_connection_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": _blocked_real_path_warnings(),
    }


def _blocked_real_path_warnings() -> list[str]:
    checks = [
        ("SHANDONG_V5_ENABLE_PROVIDER_CONNECTION", "provider connection requested but blocked in V5.19"),
        ("SHANDONG_V5_ENABLE_SANDBOX_API", "sandbox api requested but blocked in V5.19"),
        ("SHANDONG_V5_ENABLE_REAL_ORDERS", "real orders requested but blocked in V5.19"),
        ("SHANDONG_V5_ENABLE_REAL_MONEY", "real money requested but blocked in V5.19"),
    ]
    return [message for env_name, message in checks if _env_bool(env_name, False)]

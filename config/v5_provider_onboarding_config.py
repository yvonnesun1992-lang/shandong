from __future__ import annotations

import os

from config.v5_provider_selection_config import DEFAULT_PROVIDERS


VALID_ONBOARDING_MODES = {"disabled", "runbook_only", "readiness_review"}
VALID_PROVIDERS = set(DEFAULT_PROVIDERS)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_onboarding_mode() -> str:
    value = os.getenv("SHANDONG_V5_ONBOARDING_MODE", "runbook_only").strip().lower()
    return value if value in VALID_ONBOARDING_MODES else "runbook_only"


def get_selected_provider() -> str:
    value = os.getenv("SHANDONG_V5_SELECTED_PROVIDER", "").strip().lower()
    return value if value in VALID_PROVIDERS else "alpaca"


def get_onboarding_status() -> dict:
    return {
        "version": "V5.20",
        "onboarding_mode": get_onboarding_mode(),
        "selected_provider": get_selected_provider(),
        "runbook_only": True,
        "provider_portal_access_enabled": False,
        "sandbox_api_enabled": False,
        "api_key_creation_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": _blocked_real_path_warnings(),
    }


def _blocked_real_path_warnings() -> list[str]:
    checks = [
        ("SHANDONG_V5_ENABLE_PROVIDER_PORTAL_ACCESS", "provider portal access requested but blocked in V5.20"),
        ("SHANDONG_V5_ENABLE_SANDBOX_API", "sandbox api requested but blocked in V5.20"),
        ("SHANDONG_V5_ENABLE_API_KEY_CREATION", "api key creation requested but blocked in V5.20"),
        ("SHANDONG_V5_ENABLE_REAL_ORDERS", "real orders requested but blocked in V5.20"),
        ("SHANDONG_V5_ENABLE_REAL_MONEY", "real money requested but blocked in V5.20"),
    ]
    return [message for env_name, message in checks if _env_bool(env_name, False)]

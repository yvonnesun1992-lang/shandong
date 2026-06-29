from __future__ import annotations

import os

from config.v5_provider_selection_config import DEFAULT_PROVIDERS
from provider_onboarding.selected_provider_resolver import build_selected_provider_summary


VALID_CONNECTOR_DESIGN_MODES = {"disabled", "design_only", "readiness_review"}
VALID_PROVIDERS = set(DEFAULT_PROVIDERS)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_connector_design_mode() -> str:
    value = os.getenv("SHANDONG_V5_CONNECTOR_DESIGN_MODE", "design_only").strip().lower()
    return value if value in VALID_CONNECTOR_DESIGN_MODES else "design_only"


def get_design_provider() -> str:
    configured = os.getenv("SHANDONG_V5_CONNECTOR_DESIGN_PROVIDER", "").strip().lower()
    if configured in VALID_PROVIDERS:
        return configured
    if configured:
        return "alpaca"
    selected = build_selected_provider_summary().get("selected_provider", "alpaca")
    return selected if selected in VALID_PROVIDERS else "alpaca"


def get_connector_design_status() -> dict:
    return {
        "version": "V5.21",
        "connector_design_mode": get_connector_design_mode(),
        "design_provider": get_design_provider(),
        "design_only": True,
        "connector_runtime_enabled": False,
        "sandbox_api_enabled": False,
        "account_read_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": _blocked_real_path_warnings(),
    }


def _blocked_real_path_warnings() -> list[str]:
    checks = [
        ("SHANDONG_V5_ENABLE_CONNECTOR_RUNTIME", "connector runtime requested but blocked in V5.21"),
        ("SHANDONG_V5_ENABLE_SANDBOX_API", "sandbox api requested but blocked in V5.21"),
        ("SHANDONG_V5_ENABLE_ACCOUNT_READ", "account read requested but blocked in V5.21"),
        ("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "order submission requested but blocked in V5.21"),
        ("SHANDONG_V5_ENABLE_REAL_MONEY", "real money requested but blocked in V5.21"),
    ]
    return [message for env_name, message in checks if _env_bool(env_name, False)]

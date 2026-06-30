from __future__ import annotations

import os


SUPPORTED_PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_controlled_enablement_mode() -> str:
    return "controlled_blueprint_only"


def get_controlled_enablement_provider() -> str:
    provider = os.getenv("SHANDONG_V5_CONTROLLED_ENABLEMENT_PROVIDER")
    if not provider:
        try:
            from config.v5_sandbox_preflight_packet_config import get_preflight_packet_provider

            provider = get_preflight_packet_provider()
        except Exception:
            provider = "alpaca"
    return provider if provider in SUPPORTED_PROVIDERS else "alpaca"


def get_controlled_enablement_status() -> dict:
    warnings: list[str] = []
    requested_flags = {
        "SHANDONG_V5_ENABLE_CONTROLLED_RUNTIME": "controlled runtime requested but blocked in V5.32",
        "SHANDONG_V5_ENABLE_CONTROLLED_GO": "controlled go requested but blocked in V5.32",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.32",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.32",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.32",
        "SHANDONG_V5_ENABLE_ORDER_PREVIEW": "order preview requested but blocked in V5.32",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.32",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.32",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)

    return {
        "version": "V5.32",
        "controlled_enablement_mode": get_controlled_enablement_mode(),
        "provider": get_controlled_enablement_provider(),
        "controlled_blueprint_only": True,
        "controlled_enablement_runtime_enabled": False,
        "controlled_go_enabled": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "order_preview_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": warnings,
    }

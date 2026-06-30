from __future__ import annotations

import os


SUPPORTED_PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_preflight_packet_mode() -> str:
    return "preflight_packet_only"


def get_preflight_packet_provider() -> str:
    provider = os.getenv("SHANDONG_V5_PREFLIGHT_PACKET_PROVIDER")
    if not provider:
        try:
            from config.v5_sandbox_review_board_config import get_review_board_provider

            provider = get_review_board_provider()
        except Exception:
            provider = "alpaca"
    return provider if provider in SUPPORTED_PROVIDERS else "alpaca"


def get_preflight_packet_status() -> dict:
    warnings: list[str] = []
    requested_flags = {
        "SHANDONG_V5_ENABLE_PREFLIGHT_RUNTIME": "preflight runtime requested but blocked in V5.31",
        "SHANDONG_V5_ENABLE_PACKET_APPROVAL": "packet approval requested but blocked in V5.31",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.31",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.31",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.31",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.31",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.31",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)

    return {
        "version": "V5.31",
        "preflight_packet_mode": get_preflight_packet_mode(),
        "provider": get_preflight_packet_provider(),
        "preflight_packet_only": True,
        "preflight_runtime_enabled": False,
        "packet_approval_enabled": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": warnings,
    }

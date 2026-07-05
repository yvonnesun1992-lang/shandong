from __future__ import annotations

import os


VERSION = "V5.44"
BRAND_MODE = "brand_system_only"


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_brand_mode() -> str:
    return BRAND_MODE


def get_brand_assets() -> dict:
    return {
        "brand_name": "Shandong Quantitative System",
        "brand_name_cn": "山洞量化系统",
        "brand_logo": "gold_mountain_candlestick_style",
        "logo_asset": "/brand/shandong-quant-logo.png",
        "primary_color": "deep_navy",
        "accent_color": "gold",
        "theme": "institutional_quant",
    }


def get_brand_status() -> dict:
    warnings: list[str] = []
    requested_mode = os.getenv("SHANDONG_V5_BRAND_SYSTEM_MODE", "").strip()
    if requested_mode and requested_mode != BRAND_MODE:
        warnings.append("brand system mode override requested but blocked in V5.44")

    requested_flags = {
        "SHANDONG_V5_ENABLE_BRAND_RUNTIME": "brand runtime requested but blocked in V5.44",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.44",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.44",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.44",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.44",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.44",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)

    return {
        "version": VERSION,
        "brand_mode": get_brand_mode(),
        "brand_system_only": True,
        "brand_runtime_enabled": False,
        "assets": get_brand_assets(),
        "broker_connected": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "balance_read_enabled": False,
        "position_read_enabled": False,
        "order_preview_enabled": False,
        "order_submission_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": warnings,
    }

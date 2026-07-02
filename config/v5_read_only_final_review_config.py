from __future__ import annotations

import os

SUPPORTED_PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_read_only_final_review_mode() -> str:
    return "read_only_final_review_only"


def get_read_only_final_review_provider() -> str:
    provider = os.getenv("SHANDONG_V5_READ_ONLY_FINAL_REVIEW_PROVIDER")
    if not provider:
        try:
            from config.v5_read_only_evidence_pack_config import get_read_only_evidence_pack_provider

            provider = get_read_only_evidence_pack_provider()
        except Exception:
            provider = "alpaca"
    return provider if provider in SUPPORTED_PROVIDERS else "alpaca"


def get_read_only_final_review_status() -> dict:
    warnings: list[str] = []
    requested_mode = os.getenv("SHANDONG_V5_READ_ONLY_FINAL_REVIEW_MODE")
    if requested_mode and requested_mode.strip() != "read_only_final_review_only":
        warnings.append("read-only final review mode override requested but blocked in V5.38")
    requested_flags = {
        "SHANDONG_V5_ENABLE_READ_ONLY_FINAL_REVIEW_RUNTIME": "final review runtime requested but blocked in V5.38",
        "SHANDONG_V5_ENABLE_FINAL_REVIEW_PASS": "final review pass requested but blocked in V5.38",
        "SHANDONG_V5_ENABLE_READ_ONLY_CONNECTOR": "read-only connector requested but blocked in V5.38",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.38",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.38",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.38",
        "SHANDONG_V5_ENABLE_POSITION_READ": "position read requested but blocked in V5.38",
        "SHANDONG_V5_ENABLE_BALANCE_READ": "balance read requested but blocked in V5.38",
        "SHANDONG_V5_ENABLE_ORDER_PREVIEW": "order preview requested but blocked in V5.38",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.38",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.38",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)
    return {
        "version": "V5.38",
        "read_only_final_review_mode": get_read_only_final_review_mode(),
        "provider": get_read_only_final_review_provider(),
        "read_only_final_review_only": True,
        "final_review_runtime_enabled": False,
        "final_review_passed": False,
        "read_only_connector_allowed": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "position_read_enabled": False,
        "balance_read_enabled": False,
        "order_preview_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": warnings,
    }

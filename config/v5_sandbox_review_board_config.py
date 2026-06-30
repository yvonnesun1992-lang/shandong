from __future__ import annotations

import os


SUPPORTED_PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_review_board_mode() -> str:
    return "review_board_only"


def get_review_board_provider() -> str:
    provider = os.getenv("SHANDONG_V5_REVIEW_BOARD_PROVIDER")
    if not provider:
        try:
            from config.v5_sandbox_dry_run_launch_config import get_dry_run_launch_provider

            provider = get_dry_run_launch_provider()
        except Exception:
            provider = "alpaca"
    return provider if provider in SUPPORTED_PROVIDERS else "alpaca"


def get_review_board_status() -> dict:
    warnings: list[str] = []
    requested_flags = {
        "SHANDONG_V5_ENABLE_REVIEW_RUNTIME": "review runtime requested but blocked in V5.30",
        "SHANDONG_V5_ENABLE_REVIEWER_APPROVAL": "reviewer approval requested but blocked in V5.30",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.30",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.30",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.30",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.30",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.30",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)

    return {
        "version": "V5.30",
        "review_board_mode": get_review_board_mode(),
        "provider": get_review_board_provider(),
        "review_board_only": True,
        "review_runtime_enabled": False,
        "reviewer_approval_enabled": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": warnings,
    }

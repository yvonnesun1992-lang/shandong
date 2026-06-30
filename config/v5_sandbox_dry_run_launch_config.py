from __future__ import annotations

import os


SUPPORTED_PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_dry_run_launch_mode() -> str:
    requested = os.getenv("SHANDONG_V5_DRY_RUN_LAUNCH_MODE", "launch_plan_only")
    return "launch_plan_only" if requested else "launch_plan_only"


def get_dry_run_launch_provider() -> str:
    provider = os.getenv("SHANDONG_V5_DRY_RUN_PROVIDER")
    if not provider:
        try:
            from config.v5_pre_sandbox_approval_config import get_pre_sandbox_approval_provider

            provider = get_pre_sandbox_approval_provider()
        except Exception:
            provider = "alpaca"
    return provider if provider in SUPPORTED_PROVIDERS else "alpaca"


def get_dry_run_launch_status() -> dict:
    warnings: list[str] = []
    requested_flags = {
        "SHANDONG_V5_ENABLE_DRY_RUN_RUNTIME": "dry-run runtime requested but blocked in V5.29",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.29",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.29",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.29",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.29",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.29",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)

    return {
        "version": "V5.29",
        "dry_run_launch_mode": get_dry_run_launch_mode(),
        "provider": get_dry_run_launch_provider(),
        "launch_plan_only": True,
        "launch_runtime_enabled": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": warnings,
    }

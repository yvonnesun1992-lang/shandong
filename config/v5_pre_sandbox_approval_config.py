from __future__ import annotations

import os


SUPPORTED_PROVIDERS = {"alpaca", "ibkr", "futu", "tiger", "schwab"}


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_pre_sandbox_approval_mode() -> str:
    return "approval_gate_only"


def get_pre_sandbox_approval_provider() -> str:
    try:
        from config.v5_credential_vault_design_config import get_vault_design_provider

        provider = get_vault_design_provider()
    except Exception:
        provider = os.getenv("SHANDONG_V5_PRE_SANDBOX_PROVIDER", "alpaca")
    return provider if provider in SUPPORTED_PROVIDERS else "alpaca"


def get_pre_sandbox_approval_status() -> dict:
    warnings: list[str] = []
    requested_flags = {
        "SHANDONG_V5_OPERATOR_APPROVAL_GRANTED": "simulated operator approval requested but blocked in V5.28",
        "SHANDONG_V5_ENABLE_APPROVAL_RUNTIME": "approval runtime requested but blocked in V5.28",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.28",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.28",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.28",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.28",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)

    return {
        "version": "V5.28",
        "approval_mode": get_pre_sandbox_approval_mode(),
        "provider": get_pre_sandbox_approval_provider(),
        "approval_gate_only": True,
        "approval_runtime_enabled": False,
        "operator_approval_granted": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "broker_connected": False,
        "order_submission_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": warnings,
    }

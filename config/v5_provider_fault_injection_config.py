from __future__ import annotations

import os

from config.v5_provider_offline_replay_config import get_offline_replay_provider
from config.v5_provider_selection_config import DEFAULT_PROVIDERS


VALID_FAULT_INJECTION_MODES = {"disabled", "fault_injection_only", "readiness_review"}
VALID_PROVIDERS = set(DEFAULT_PROVIDERS)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_fault_injection_mode() -> str:
    value = os.getenv("SHANDONG_V5_FAULT_INJECTION_MODE", "fault_injection_only").strip().lower()
    return value if value in VALID_FAULT_INJECTION_MODES else "fault_injection_only"


def get_fault_injection_provider() -> str:
    configured = os.getenv("SHANDONG_V5_FAULT_INJECTION_PROVIDER", "").strip().lower()
    if configured in VALID_PROVIDERS:
        return configured
    if configured:
        return "alpaca"
    provider = get_offline_replay_provider()
    return provider if provider in VALID_PROVIDERS else "alpaca"


def get_fault_injection_status() -> dict:
    return {
        "version": "V5.24",
        "fault_injection_mode": get_fault_injection_mode(),
        "fault_injection_provider": get_fault_injection_provider(),
        "fault_injection_only": True,
        "fault_injection_runtime_enabled": False,
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
        ("SHANDONG_V5_ENABLE_FAULT_INJECTION_RUNTIME", "fault injection runtime requested but blocked in V5.24"),
        ("SHANDONG_V5_ENABLE_SANDBOX_API", "sandbox api requested but blocked in V5.24"),
        ("SHANDONG_V5_ENABLE_ACCOUNT_READ", "account read requested but blocked in V5.24"),
        ("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "order submission requested but blocked in V5.24"),
        ("SHANDONG_V5_ENABLE_REAL_MONEY", "real money requested but blocked in V5.24"),
    ]
    return [message for env_name, message in checks if _env_bool(env_name, False)]

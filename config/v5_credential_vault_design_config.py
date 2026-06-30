from __future__ import annotations

import os

from config.v5_sandbox_readiness_evidence_config import get_evidence_provider
from config.v5_provider_selection_config import DEFAULT_PROVIDERS


VALID_VAULT_DESIGN_MODES = {"disabled", "vault_design_only", "readiness_review"}
VALID_PROVIDERS = set(DEFAULT_PROVIDERS)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_vault_design_mode() -> str:
    value = os.getenv("SHANDONG_V5_VAULT_DESIGN_MODE", "vault_design_only").strip().lower()
    return value if value in VALID_VAULT_DESIGN_MODES else "vault_design_only"


def get_vault_design_provider() -> str:
    configured = os.getenv("SHANDONG_V5_VAULT_DESIGN_PROVIDER", "").strip().lower()
    if configured in VALID_PROVIDERS:
        return configured
    if configured:
        return "alpaca"
    provider = get_evidence_provider()
    return provider if provider in VALID_PROVIDERS else "alpaca"


def get_vault_design_status() -> dict:
    return {
        "version": "V5.27",
        "vault_design_mode": get_vault_design_mode(),
        "vault_design_provider": get_vault_design_provider(),
        "vault_design_only": True,
        "vault_runtime_enabled": False,
        "secret_read_enabled": False,
        "secret_write_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "order_submission_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": _blocked_real_path_warnings(),
    }


def _blocked_real_path_warnings() -> list[str]:
    checks = [
        ("SHANDONG_V5_ENABLE_VAULT_RUNTIME", "vault runtime requested but blocked in V5.27"),
        ("SHANDONG_V5_ENABLE_SECRET_READ", "secret read requested but blocked in V5.27"),
        ("SHANDONG_V5_ENABLE_SECRET_WRITE", "secret write requested but blocked in V5.27"),
        ("SHANDONG_V5_ENABLE_SANDBOX_API", "sandbox api requested but blocked in V5.27"),
        ("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "order submission requested but blocked in V5.27"),
        ("SHANDONG_V5_ENABLE_REAL_MONEY", "real money requested but blocked in V5.27"),
    ]
    return [message for env_name, message in checks if _env_bool(env_name, False)]

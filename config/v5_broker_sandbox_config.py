from __future__ import annotations

import os


VALID_SANDBOX_MODES = {"disabled", "planned", "readiness_only"}
VALID_SANDBOX_PROVIDERS = {
    "none",
    "alpaca_sandbox_planned",
    "ibkr_paper_planned",
    "futu_sim_planned",
    "tiger_sim_planned",
    "schwab_sandbox_planned",
}
VALID_CREDENTIAL_POLICIES = {"not_configured", "vault_planned", "env_planned"}


def get_sandbox_mode() -> str:
    return _choice(os.getenv("SHANDONG_V5_SANDBOX_MODE"), VALID_SANDBOX_MODES, "planned")


def get_sandbox_provider_plan() -> str:
    return _choice(os.getenv("SHANDONG_V5_SANDBOX_PROVIDER"), VALID_SANDBOX_PROVIDERS, "none")


def get_sandbox_credential_policy() -> str:
    return _choice(os.getenv("SHANDONG_V5_SANDBOX_CREDENTIAL_POLICY"), VALID_CREDENTIAL_POLICIES, "not_configured")


def get_sandbox_order_policy() -> dict:
    return {
        "sandbox_connection_enabled": False,
        "sandbox_orders_enabled": False,
        "sandbox_order_submission_policy": "rejected_by_default",
        "order_release_policy": "planned_only",
        "manual_approval_required": True,
        "kill_switch_required": True,
        "audit_required": True,
        "paper_trading": True,
        "planning_only": True,
    }


def get_sandbox_readiness_status() -> dict:
    return {
        "version": "V5.10",
        "sandbox_mode": get_sandbox_mode(),
        "sandbox_provider": get_sandbox_provider_plan(),
        "sandbox_credential_policy": get_sandbox_credential_policy(),
        "sandbox_connection_enabled": False,
        "sandbox_orders_enabled": False,
        "real_broker_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "warning": [
            "broker sandbox readiness planning only",
            "sandbox connection disabled",
            "sandbox order submission disabled",
        ],
    }


def _choice(value: str | None, allowed: set[str], default: str) -> str:
    if not value:
        return default
    normalized = value.strip().lower()
    return normalized if normalized in allowed else default

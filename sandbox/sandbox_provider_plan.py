from __future__ import annotations


PROVIDERS = [
    "alpaca_sandbox_planned",
    "ibkr_paper_planned",
    "futu_sim_planned",
    "tiger_sim_planned",
    "schwab_sandbox_planned",
]


def list_sandbox_provider_plans() -> list[dict]:
    return [build_sandbox_provider_plan(provider) for provider in PROVIDERS]


def build_sandbox_provider_plan(provider: str = "none") -> dict:
    selected = provider if provider in PROVIDERS else "none"
    return {
        "provider": selected,
        "status": "planned_only",
        "sdk_required": selected != "none",
        "credential_required": selected != "none",
        "manual_approval_required": True,
        "kill_switch_required": True,
        "audit_required": True,
        "sandbox_connection_enabled": False,
        "sandbox_orders_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "readiness": "planned" if selected != "none" else "not_ready",
        "warnings": ["provider planning only", "no external SDK imported", "no external API connection"],
    }

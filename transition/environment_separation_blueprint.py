from __future__ import annotations


def build_environment_separation_blueprint() -> dict:
    environments = []
    for name in ["local", "test", "staging", "sandbox", "production"]:
        environments.append(
            {
                "environment": name,
                "allowed_data": "mock/paper" if name in {"local", "test", "staging"} else "planned only",
                "allowed_orders": "paper only" if name != "production" else "disabled",
                "broker_connection_allowed": False,
                "real_orders_allowed": False,
                "credential_source": "none" if name != "production" else "future vault only",
                "logging_policy": "sanitized local logs" if name != "production" else "future managed audit logs",
                "approval_policy": "manual approval required before future enablement",
                "kill_switch_required": True,
                "rollback_required": True,
            }
        )
    return {
        "version": "V5.18",
        "blueprint_only": True,
        "transition_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "environments": environments,
    }

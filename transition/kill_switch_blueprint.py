from __future__ import annotations


def build_kill_switch_blueprint() -> dict:
    controls = [
        "global kill switch",
        "strategy kill switch",
        "broker connector kill switch",
        "order submission kill switch",
        "account read kill switch",
        "emergency stop runbook",
        "operator confirmation",
        "audit event",
        "rollback trigger",
    ]
    return {
        "version": "V5.18",
        "blueprint_only": True,
        "controls": controls,
        "execution_enabled": False,
        "external_notification_enabled": False,
        "transition_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }

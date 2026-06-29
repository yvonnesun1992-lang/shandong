from __future__ import annotations


def build_rollback_blueprint() -> dict:
    steps = [
        "disable connector flags",
        "freeze order queue",
        "cancel pending sandbox orders planned",
        "stop new signals",
        "switch to paper-only",
        "restore checkpoint",
        "write audit event",
        "operator notification placeholder",
        "postmortem checklist",
    ]
    return {
        "version": "V5.18",
        "blueprint_only": True,
        "steps": steps,
        "executes_broker_cancel": False,
        "external_notification_enabled": False,
        "transition_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }

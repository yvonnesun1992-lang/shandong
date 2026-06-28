from __future__ import annotations


def build_sandbox_rollback_plan() -> dict:
    steps = [
        "disable sandbox connection",
        "disable sandbox order submission",
        "switch to paper-only mode",
        "clear pending sandbox order queue",
        "freeze manual approval queue",
        "notify operator placeholder",
        "write audit event",
        "restore last safe checkpoint",
        "generate rollback report",
    ]
    return {
        "steps": steps,
        "executes_broker_cancel": False,
        "external_notification_enabled": False,
        "log_upload_enabled": False,
        "calls_external_broker": False,
        "sandbox_connection_enabled": False,
        "sandbox_orders_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "warnings": ["rollback plan is documentation only", "no external broker cancel API is called"],
    }

from __future__ import annotations


LIFECYCLE_STAGES = [
    "alpha_signal_generated",
    "paper_order_created",
    "risk_gate_checked",
    "manual_approval_required",
    "sandbox_order_preview_created",
    "sandbox_order_submission_planned",
    "broker_response_planned",
    "audit_event_recorded",
    "kill_switch_checked",
]


def build_sandbox_order_lifecycle_plan() -> dict:
    return {
        "stages": [{"name": stage, "status": "planned_only"} for stage in LIFECYCLE_STAGES],
        "sandbox_order_submission_enabled": False,
        "sandbox_order_release_enabled": False,
        "order_release_policy": "planned_only",
        "sandbox_order": None,
        "real_broker_order": None,
        "sandbox_order_generated": False,
        "real_order_generated": False,
        "sandbox_connection_enabled": False,
        "sandbox_orders_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "warnings": ["sandbox order lifecycle is documentation only", "all release paths are rejected by default"],
    }

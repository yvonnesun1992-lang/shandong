from __future__ import annotations


CHECKLIST_ITEMS = [
    "V5.17 integration test PASS",
    "V5.12 robustness PASS or WARNING accepted",
    "credential vault ready",
    "sandbox account approved",
    "manual approval workflow ready",
    "kill switch ready",
    "risk limits configured",
    "audit logging immutable",
    "rollback runbook approved",
    "legal / compliance reviewed",
    "operator trained",
    "dry run scheduled",
]


def build_sandbox_enablement_checklist() -> dict:
    checklist = [{"item": item, "complete": False, "owner": "future_operator"} for item in CHECKLIST_ITEMS]
    return {
        "version": "V5.18",
        "blueprint_only": True,
        "ready_to_enable_sandbox_api": False,
        "ready_to_submit_sandbox_orders": False,
        "blocking_items": CHECKLIST_ITEMS,
        "warnings": [],
        "checklist": checklist,
        "transition_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }

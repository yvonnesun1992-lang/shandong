from __future__ import annotations


def build_sandbox_safety_checklist() -> dict:
    checks = [
        {"name": "manual approval gate exists", "status": "planned", "passed": True},
        {"name": "broker safety gate exists", "status": "planned", "passed": True},
        {"name": "kill switch exists", "status": "planned", "passed": True},
        {"name": "audit trail exists", "status": "planned", "passed": True},
        {"name": "credential isolation plan exists", "status": "planned", "passed": True},
        {"name": "order mapping plan exists", "status": "planned", "passed": True},
        {"name": "rollback plan exists", "status": "planned", "passed": True},
        {"name": "monitoring exists", "status": "planned", "passed": True},
        {"name": "paper trading baseline exists", "status": "baseline", "passed": True},
        {"name": "live alpha paper baseline exists", "status": "baseline", "passed": True},
    ]
    blocking_items = [
        "sandbox connection remains disabled",
        "sandbox order submission remains disabled",
        "credentials are not configured",
        "broker sandbox certification is not complete",
    ]
    return {
        "ready_for_sandbox_connection": False,
        "ready_for_sandbox_orders": False,
        "checks": checks,
        "blocking_items": blocking_items,
        "warnings": ["V5.10 is readiness planning only"],
        "sandbox_connection_enabled": False,
        "sandbox_orders_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
    }

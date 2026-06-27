from __future__ import annotations

from typing import Any

from config.v5_broker_integration_config import get_broker_integration_status


def validate_broker_safety() -> dict[str, Any]:
    status = get_broker_integration_status()
    checks = [
        {"name": "broker_connected_false", "passed": status["broker_connected"] is False},
        {"name": "real_orders_disabled", "passed": status["real_orders_enabled"] is False},
        {"name": "real_money_disabled", "passed": status["real_money_enabled"] is False},
        {"name": "manual_approval_required_planned", "passed": True},
        {"name": "kill_switch_required_planned", "passed": True},
        {"name": "position_limit_required_planned", "passed": True},
    ]
    return {
        "safe": all(item["passed"] for item in checks),
        "checks": checks,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "manual_approval_required": "planned",
        "kill_switch_required": "planned",
        "position_limit_required": "planned",
        "paper_trading": True,
        "planning_only": True,
        "warnings": ["future live broker access requires a separate safety review"],
    }


def reject_real_order_attempt(order: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "status": "rejected",
        "reason": "broker integration planned only",
        "real_order_submitted": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "order_preview": _safe_preview(order or {}),
    }


def broker_readiness_summary() -> dict[str, Any]:
    safety = validate_broker_safety()
    return {
        "readiness": "planning_only" if safety["safe"] else "not_ready_for_live_broker",
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "required_before_live": [
            "manual approval workflow",
            "independent kill switch",
            "position and notional limits",
            "sandbox certification",
            "credential vault design outside repository",
            "legal and operational review",
        ],
        "safety": safety,
    }


def _safe_preview(order: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol": str(order.get("symbol", "")),
        "side": str(order.get("side", order.get("action", ""))).upper(),
        "quantity": order.get("quantity"),
    }

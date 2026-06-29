from __future__ import annotations


def build_real_order_blocker_policy() -> dict:
    return {
        "version": "V5.18",
        "blocked": True,
        "reason": "real order path disabled in V5.18",
        "manual_approval_cannot_release_real_order": True,
        "requires_future_release_stage": True,
        "real_order_submitted": False,
        "real_money_enabled": False,
        "broker_connected": False,
        "sandbox_api_enabled": False,
        "blueprint_only": True,
        "transition_enabled": False,
        "real_orders_enabled": False,
        "paper_trading": True,
    }


def evaluate_real_order_attempt(context: dict | None = None) -> dict:
    _ = context or {}
    return {
        "blocked": True,
        "reason": "real order path disabled in V5.18",
        "real_order_submitted": False,
        "real_money_enabled": False,
        "broker_connected": False,
        "sandbox_api_enabled": False,
        "manual_approval_overridden": False,
        "blueprint_only": True,
        "transition_enabled": False,
        "real_orders_enabled": False,
        "paper_trading": True,
    }

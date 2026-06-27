from __future__ import annotations

import os


VALID_MODES = {"disabled", "planned", "simulated"}


def get_manual_approval_mode() -> str:
    value = os.getenv("SHANDONG_V5_MANUAL_APPROVAL_MODE", "planned").strip().lower()
    return value if value in VALID_MODES else "planned"


def get_manual_approval_required() -> bool:
    return True


def get_manual_approval_policy() -> dict:
    return {
        "manual_approval_required": True,
        "auto_approval_enabled": False,
        "real_order_after_approval": False,
        "real_orders_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "reject_by_default": True,
        "allowed_simulated_approval_status": "APPROVED_SIMULATED",
        "blocked_statuses": ["AUTO_APPROVED", "LIVE_APPROVED", "REAL_ORDER_READY"],
    }


def get_manual_approval_status() -> dict:
    return {
        "version": "V5.9",
        "manual_approval_mode": get_manual_approval_mode(),
        "manual_approval_required": get_manual_approval_required(),
        "auto_approval_enabled": False,
        "real_order_after_approval": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "warning": [
            "manual approval gate planning only",
            "auto approval disabled",
            "real order release disabled after simulated approval",
        ],
    }

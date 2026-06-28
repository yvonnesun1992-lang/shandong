from __future__ import annotations

from datetime import UTC, datetime


MOCK_ORDER_STATUSES = {
    "MOCK_CREATED",
    "MOCK_ACCEPTED",
    "MOCK_PARTIALLY_FILLED",
    "MOCK_FILLED",
    "MOCK_REJECTED",
    "MOCK_CANCELED",
    "MOCK_EXPIRED",
    "MOCK_RATE_LIMITED",
    "MOCK_DUPLICATE",
}

BLOCKED_REAL_ORDER_STATUSES = {
    "LIVE_SUBMITTED",
    "REAL_ORDER_READY",
    "BROKER_ACCEPTED_REAL",
    "REAL_FILLED",
    "REAL_CANCELED",
}


def transition_mock_order(order: dict, target_status: str, reason: str = "") -> dict:
    validation = validate_mock_order_status(target_status)
    if not validation["valid"]:
        return {
            "accepted": False,
            "order": {**order},
            "reason": validation["reason"],
            "mock_only": True,
            "real_order_submitted": False,
        }
    updated = {**order, "status": target_status, "updated_at": _now(), "reason": reason or _default_reason(target_status)}
    return {"accepted": True, "order": updated, "mock_only": True, "real_order_submitted": False}


def validate_mock_order_status(status: str) -> dict:
    if status in MOCK_ORDER_STATUSES:
        return {"valid": True, "status": status, "reason": "mock status accepted", "mock_only": True}
    if status in BLOCKED_REAL_ORDER_STATUSES:
        return {"valid": False, "status": status, "reason": "blocked non-mock status", "mock_only": True}
    return {"valid": False, "status": status, "reason": "unknown status", "mock_only": True}


def build_mock_order_lifecycle_policy() -> dict:
    return {
        "version": "V5.14",
        "mock_statuses": sorted(MOCK_ORDER_STATUSES),
        "blocked_non_mock_statuses": sorted(BLOCKED_REAL_ORDER_STATUSES),
        "real_order_path_allowed": False,
        "mock_only": True,
        "paper_trading": True,
    }


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _default_reason(status: str) -> str:
    return {
        "MOCK_CREATED": "mock order created",
        "MOCK_ACCEPTED": "mock order accepted",
        "MOCK_PARTIALLY_FILLED": "mock partial fill",
        "MOCK_FILLED": "mock order filled",
        "MOCK_REJECTED": "mock order rejected",
        "MOCK_CANCELED": "mock order canceled",
        "MOCK_EXPIRED": "mock order expired",
        "MOCK_RATE_LIMITED": "mock rate limit response",
        "MOCK_DUPLICATE": "mock duplicate response",
    }.get(status, "mock transition")

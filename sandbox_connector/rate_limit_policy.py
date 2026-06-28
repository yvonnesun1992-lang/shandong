from __future__ import annotations


LIMITS = {"submit_order": 5, "cancel_order": 10, "order_status": 60, "account_snapshot": 30}


def build_rate_limit_policy() -> dict:
    return {"limits_per_minute": LIMITS.copy(), "external_calls": False, "contract_only": True}


def check_rate_limit(action: str, request_count: int, window_seconds: int = 60) -> dict:
    limit = LIMITS.get(action, 30)
    allowed = request_count <= limit or window_seconds < 60
    return {"allowed": allowed, "error_code": None if allowed else "RATE_LIMITED", "limit": limit, "contract_only": True}


def build_backoff_schedule() -> dict:
    return {"schedule_seconds": [1, 2, 4], "sleep_called": False, "contract_only": True}

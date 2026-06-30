from __future__ import annotations

from sandbox_read_only_connector.init import boundary


def build_read_only_rate_limit_policy(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "account_snapshot_read_budget_placeholder": "READ_BUDGET_PLACEHOLDER",
        "balance_read_budget_placeholder": "READ_BUDGET_PLACEHOLDER",
        "position_read_budget_placeholder": "READ_BUDGET_PLACEHOLDER",
        "order_history_read_budget_placeholder": "READ_BUDGET_PLACEHOLDER",
        "cooldown_policy": "placeholder cooldown only",
        "backoff_policy": "placeholder backoff only",
        "circuit_breaker": "placeholder circuit breaker only",
        "write_request_budget": 0,
        "network_calls_enabled": False,
    }

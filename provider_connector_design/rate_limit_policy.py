from __future__ import annotations

from provider_connector_design import boundary


def build_rate_limit_policy(provider: str) -> dict:
    return {
        "provider": provider,
        "rate_limit_policy": {
            "request_budget": "request_budget_placeholder",
            "order_submission_rate_limit": "order_submission_rate_limit_placeholder",
            "account_read_rate_limit": "account_read_rate_limit_placeholder",
            "market_data_rate_limit": "market_data_rate_limit_placeholder",
            "burst_limit": "burst_limit_placeholder",
            "cooldown_policy": "cooldown_after_limit_placeholder",
            "backoff_policy": "exponential_backoff_placeholder",
            "queueing_policy": "local_queue_placeholder",
            "circuit_breaker_policy": "open_circuit_on_repeated_failures_placeholder",
        },
        "requires_future_provider_docs": True,
        "network_calls_enabled": False,
        **boundary(),
    }

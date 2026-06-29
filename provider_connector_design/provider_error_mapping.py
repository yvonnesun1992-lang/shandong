from __future__ import annotations

from provider_connector_design import boundary


ERROR_TYPES = [
    "AUTH_ERROR",
    "PERMISSION_DENIED",
    "RATE_LIMITED",
    "INVALID_SYMBOL",
    "INVALID_ORDER",
    "INSUFFICIENT_FUNDS",
    "MARKET_CLOSED",
    "DUPLICATE_ORDER",
    "ORDER_REJECTED",
    "ORDER_NOT_FOUND",
    "NETWORK_UNAVAILABLE",
    "PROVIDER_TIMEOUT",
    "UNKNOWN_PROVIDER_ERROR",
]


def build_provider_error_mapping(provider: str) -> dict:
    return {
        "provider": provider,
        "error_mapping": {error_type: f"provider_{error_type.lower()}_placeholder" for error_type in ERROR_TYPES},
        "retryable_errors": ["RATE_LIMITED", "NETWORK_UNAVAILABLE", "PROVIDER_TIMEOUT"],
        "non_retryable_errors": ["AUTH_ERROR", "PERMISSION_DENIED", "INVALID_SYMBOL", "INVALID_ORDER", "INSUFFICIENT_FUNDS"],
        "manual_review_required_errors": ["ORDER_REJECTED", "ORDER_NOT_FOUND", "UNKNOWN_PROVIDER_ERROR"],
        **boundary(),
    }

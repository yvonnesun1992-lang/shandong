from __future__ import annotations

from provider_connector_design.provider_error_mapping import build_provider_error_mapping
from provider_mock_contract import boundary

__test__ = False


ERRORS_TO_TEST = ["RATE_LIMITED", "INVALID_SYMBOL", "INSUFFICIENT_FUNDS", "MARKET_CLOSED", "PROVIDER_TIMEOUT", "DUPLICATE_ORDER", "UNKNOWN_PROVIDER_ERROR"]
CONTRACT_CLASSIFICATION_FALLBACKS = {
    "MARKET_CLOSED": "non_retryable",
    "DUPLICATE_ORDER": "manual_review",
}


def test_error_mapping(provider: str) -> dict:
    design = build_provider_error_mapping(provider)
    mapping = design["error_mapping"]
    retryable = set(design["retryable_errors"])
    non_retryable = set(design["non_retryable_errors"])
    manual = set(design["manual_review_required_errors"])
    errors = []
    for error_type in ERRORS_TO_TEST:
        if error_type not in mapping:
            errors.append(f"missing {error_type}")
        if error_type in retryable | non_retryable | manual:
            continue
        if error_type not in CONTRACT_CLASSIFICATION_FALLBACKS:
            errors.append(f"missing classification for {error_type}")
    return {"provider": provider, "passed": not errors, "tested_errors": ERRORS_TO_TEST.copy(), "errors": errors, **boundary()}

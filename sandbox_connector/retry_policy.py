from __future__ import annotations


RETRYABLE = {"TIMEOUT", "PROVIDER_UNAVAILABLE", "RATE_LIMITED"}
NON_RETRYABLE = {"ORDER_REJECTED", "RISK_REJECTED", "MANUAL_APPROVAL_REQUIRED", "KILL_SWITCH_ACTIVE"}
MAX_ATTEMPTS = 3


def build_retry_policy() -> dict:
    return {"retryable": sorted(RETRYABLE), "non_retryable": sorted(NON_RETRYABLE), "max_attempts": MAX_ATTEMPTS, "sleep_called": False, "contract_only": True}


def should_retry(error_code: str, attempt: int) -> dict:
    retry = error_code in RETRYABLE and attempt < MAX_ATTEMPTS
    return {"retry": retry, "error_code": error_code, "attempt": attempt, "contract_only": True}


def next_retry_delay(error_code: str, attempt: int) -> dict:
    return {"delay_seconds": min(2 ** max(attempt - 1, 0), 4) if error_code in RETRYABLE else 0, "sleep_called": False, "contract_only": True}

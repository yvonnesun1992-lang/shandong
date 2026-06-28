from __future__ import annotations

from sandbox_bridge.sanitizer import bridge_boundary


RETRYABLE = {"TIMEOUT", "RATE_LIMITED"}
NON_RETRYABLE = {"ORDER_REJECTED", "REJECTED", "RISK_REJECTED", "CREDENTIAL_INVALID"}
MAX_RETRY = 3


def should_retry(error_code: str, attempt: int = 0) -> bool:
    code = str(error_code).upper()
    return code in RETRYABLE and attempt < MAX_RETRY


def compute_backoff(attempt: int) -> int:
    return min(2 ** max(int(attempt), 0), 8)


def schedule_retry(error_code: str, attempt: int = 0) -> dict:
    retry = should_retry(error_code, attempt)
    return {
        "error_code": str(error_code).upper(),
        "attempt": int(attempt),
        "should_retry": retry,
        "delay_seconds": compute_backoff(attempt) if retry else 0,
        "max_retry": MAX_RETRY,
        "real_sleep": False,
        **bridge_boundary(),
    }

from __future__ import annotations

from sandbox_read_only_fault_injection.init import boundary


def simulate_rate_limit_fault(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "fault_type": "rate_limit_error",
        "rate_limit_error": True,
        "retry_allowed": False,
        "backoff_required": True,
        "circuit_breaker_required": True,
        "network_retry_executed": False,
        "order_submitted": False,
    }


def validate_rate_limit_fault_handling(payload: dict) -> dict:
    findings = []
    if payload.get("rate_limit_error") is True:
        findings.append("rate_limit_error true")
    if payload.get("retry_allowed") is not False:
        findings.append("retry allowed unexpectedly")
    if payload.get("backoff_required") is not True:
        findings.append("backoff missing")
    if payload.get("circuit_breaker_required") is not True:
        findings.append("circuit breaker missing")
    if payload.get("network_retry_executed") is not False:
        findings.append("network retry executed")
    if payload.get("order_submitted") is not False:
        findings.append("order submitted during rate limit fault")
    return {
        **boundary(),
        "provider": payload.get("provider", "alpaca"),
        "rate_limit_fault_detected": bool(findings),
        "findings": findings,
        "warnings": findings,
    }

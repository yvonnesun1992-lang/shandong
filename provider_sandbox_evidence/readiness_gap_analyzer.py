from __future__ import annotations

from provider_sandbox_evidence import boundary


BLOCKING_GAPS = [
    "credential vault not implemented",
    "real sandbox account not approved",
    "API permission not confirmed",
    "market data permission not confirmed",
    "provider docs not validated",
    "legal / compliance not reviewed",
    "manual operator training not completed",
    "production kill switch not live-tested",
    "immutable audit storage not implemented",
    "real sandbox endpoint not configured",
]


def analyze_readiness_gaps(provider: str) -> dict:
    return {
        "provider": provider,
        "ready_for_sandbox_api": False,
        "ready_for_sandbox_orders": False,
        "blocking_gaps": BLOCKING_GAPS.copy(),
        "warnings": ["sandbox entry remains blocked by design"],
        **boundary(),
    }

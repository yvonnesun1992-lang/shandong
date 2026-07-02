from __future__ import annotations

from sandbox_read_only_final_review.init import boundary

RISK_ITEMS = [
    "credential vault not live",
    "sandbox account not verified",
    "provider docs not independently verified",
    "sandbox API endpoint not approved",
    "read-only credential scope not live",
    "market data permissions not confirmed",
    "account redaction policy not live-tested",
    "balance redaction policy not live-tested",
    "position redaction policy not live-tested",
    "immutable audit storage not live",
    "kill switch not live-tested against real connector",
    "rollback plan not executed against real connector",
    "compliance signoff not completed",
    "operator training not completed",
]


def build_risk_acceptance_matrix(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "risks": [{"name": item, "status": "blocked"} for item in RISK_ITEMS],
        "accepted_risks": [],
        "blocked_risks": RISK_ITEMS,
        "risk_acceptance_ready": False,
        "warnings": ["risk acceptance is not ready for real read-only sandbox access"],
    }


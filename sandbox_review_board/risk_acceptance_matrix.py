from __future__ import annotations

from sandbox_review_board.init import boundary


RISK_ITEMS = [
    "credential vault not live",
    "sandbox account not confirmed",
    "sandbox API endpoint not validated",
    "provider docs not independently verified",
    "market data permissions unknown",
    "audit storage not immutable",
    "kill switch not live-tested against real connector",
    "no real account read test completed",
    "no sandbox order test completed",
    "compliance review not formally signed",
]


def build_risk_acceptance_matrix(provider: str = "alpaca") -> dict:
    risks = [{"name": item, "status": "blocked", "auto_accept": False} for item in RISK_ITEMS]
    return {
        **boundary(),
        "provider": provider,
        "risks": risks,
        "accepted_risks": [],
        "blocked_risks": RISK_ITEMS,
        "risk_acceptance_ready": False,
    }

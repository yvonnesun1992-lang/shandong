from __future__ import annotations

from sandbox_controlled_enablement.init import boundary


REASONS = [
    "order submission is blocked in V5.32",
    "manual approval cannot release order submission in V5.32",
    "controlled GO cannot release order submission in V5.32",
    "sandbox and real order submission remain disabled",
]


def build_order_submission_blocker(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "blocked": True,
        "order_submission_enabled": False,
        "sandbox_order_submission_allowed": False,
        "real_order_submission_allowed": False,
        "reason": REASONS.copy(),
    }


def evaluate_order_submission_attempt(context: dict | None = None) -> dict:
    context = context or {}
    provider = context.get("provider", "alpaca")
    result = build_order_submission_blocker(provider)
    result["attempted"] = True
    result["attempt_context_ignored"] = True
    return result

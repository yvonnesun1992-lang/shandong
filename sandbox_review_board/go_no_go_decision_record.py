from __future__ import annotations

from sandbox_review_board.init import boundary


def build_go_no_go_decision(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "decision": "NO_GO",
        "sandbox_dry_run_allowed": False,
        "decision_reason": [
            "review board is design-only in V5.30",
            "sandbox API remains disabled",
            "secret read remains disabled",
            "account read remains disabled",
            "order submission remains disabled",
        ],
    }


def evaluate_review_board_decision(context: dict | None = None) -> dict:
    context = context or {}
    result = build_go_no_go_decision(context.get("provider", "alpaca"))
    if context.get("simulated_approval"):
        result["warnings"] = ["simulated approval requested but review board remains NO_GO"]
    else:
        result["warnings"] = []
    return result

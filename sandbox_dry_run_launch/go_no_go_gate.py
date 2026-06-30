from __future__ import annotations

from sandbox_dry_run_launch.init import boundary


def evaluate_go_no_go_gate(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "gate": "NO_GO",
        "dry_run_launch_allowed": False,
        "approval_gate_must_remain_blocked": True,
        "blocking_items": [
            "sandbox API remains disabled",
            "secret read remains disabled",
            "account read remains disabled",
            "order submission remains disabled",
        ],
        "warnings": ["V5.29 is a launch plan only; dry-run launch is not allowed"],
    }


def build_go_no_go_summary(provider: str = "alpaca") -> dict:
    return evaluate_go_no_go_gate(provider)

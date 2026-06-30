from __future__ import annotations

from sandbox_dry_run_launch.init import boundary


STEPS = [
    "confirm evidence pack",
    "confirm approval gate blocked",
    "confirm vault design placeholder",
    "confirm feature flags disabled",
    "confirm kill switch plan",
    "confirm rollback plan",
    "simulate dry-run start",
    "simulate read-only account check",
    "simulate order preview",
    "simulate operator approval",
    "simulate kill switch",
    "simulate rollback",
    "write launch audit placeholder",
    "post-run review",
]


def build_launch_sequence_plan(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "steps": [
            {"step": index, "name": name, "execution": "simulate_only", "real_action": False}
            for index, name in enumerate(STEPS, start=1)
        ],
    }

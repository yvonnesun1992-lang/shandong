from __future__ import annotations

from sandbox_dry_run_launch.init import boundary


def build_dry_run_rollback_plan(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "rollback_ready": False,
        "steps": [
            "disable dry-run runtime flag",
            "keep sandbox API disabled",
            "keep secret read disabled",
            "keep account read disabled",
            "keep order submission disabled",
            "freeze connector path",
            "write audit event placeholder",
            "notify operator placeholder",
            "revert to paper-only",
            "postmortem checklist",
        ],
        "all_real_paths_disabled": True,
    }

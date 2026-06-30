from __future__ import annotations

from sandbox_dry_run_launch.init import boundary


def build_dry_run_scope_definition(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "dry_run_scope": {
            "dry_run_type": "read_only_first",
            "allowed_actions_planned": [
                "load config",
                "verify vault reference placeholder",
                "validate provider connector disabled",
                "validate sandbox API disabled",
                "simulate account read plan",
                "simulate order preview plan",
                "simulate approval flow",
                "simulate kill switch",
                "simulate rollback",
            ],
            "disallowed_actions": [
                "real broker connection",
                "sandbox API connection",
                "secret read",
                "real account read",
                "sandbox account read",
                "order submission",
                "real money usage",
            ],
        },
        "ready": False,
    }

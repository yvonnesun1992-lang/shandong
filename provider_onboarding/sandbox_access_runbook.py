from __future__ import annotations

from provider_onboarding import boundary


STEPS = [
    "confirm sandbox availability",
    "confirm paper trading endpoint",
    "confirm account approval requirement",
    "confirm supported asset classes",
    "confirm API documentation",
    "confirm test environment references in future docs",
    "confirm sandbox order limitations",
    "confirm market data limitations",
    "confirm rate limits",
    "confirm support channel",
]


def build_sandbox_access_runbook(provider: str) -> dict:
    return {
        "provider": provider,
        "sandbox_access_ready": False,
        "steps": STEPS.copy(),
        "blocking_items": [
            "sandbox endpoint must remain unconfigured in V5.20",
            "sandbox connectivity cannot be tested in this phase",
            "sandbox order submission remains disabled",
        ],
        **boundary(),
    }

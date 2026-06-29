from __future__ import annotations

from provider_onboarding import boundary


STEPS = [
    "delayed data check",
    "real-time data check",
    "exchange entitlement review",
    "US equities permission",
    "HK equities permission",
    "options permission",
    "historical data permission",
    "quote frequency limits",
    "redistribution restrictions",
    "commercial usage restrictions",
    "data cost awareness",
]


def build_market_data_onboarding_runbook(provider: str) -> dict:
    return {
        "provider": provider,
        "market_data_ready": False,
        "steps": STEPS.copy(),
        "blocking_items": [
            "market data API access remains disabled",
            "exchange entitlements are not verified in V5.20",
            "commercial data usage requires future review",
        ],
        **boundary(),
    }

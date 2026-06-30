from __future__ import annotations

from sandbox_preflight_packet.init import boundary


BLOCKING_ITEMS = [
    "review board decision remains NO_GO",
    "sandbox API disabled",
    "secret read disabled",
    "account read disabled",
    "order submission disabled",
    "credential vault not live",
    "sandbox account not verified",
    "provider docs not independently verified",
    "market data permissions not confirmed",
    "compliance signoff not completed",
    "immutable audit storage not live",
    "kill switch not tested against real connector",
    "rollback plan not executed against real connector",
]


def build_blocking_item_register(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "blocking_items": list(BLOCKING_ITEMS),
        "blocking_count": len(BLOCKING_ITEMS),
        "sandbox_dry_run_blocked": True,
    }

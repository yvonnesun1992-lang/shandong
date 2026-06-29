from __future__ import annotations

from provider_selection import PROVIDER_BOUNDARY


PROVIDER_METADATA = {
    "alpaca": {"region": "US", "asset_classes": ["us_equities", "crypto"], "sandbox_available": "yes", "paper_trading_available": "yes"},
    "ibkr": {"region": "global", "asset_classes": ["equities", "options", "futures", "forex"], "sandbox_available": "partial", "paper_trading_available": "yes"},
    "futu": {"region": "HK/US", "asset_classes": ["hk_equities", "us_equities", "options"], "sandbox_available": "partial", "paper_trading_available": "partial"},
    "tiger": {"region": "HK/US/SG", "asset_classes": ["equities", "options"], "sandbox_available": "unknown", "paper_trading_available": "partial"},
    "schwab": {"region": "US", "asset_classes": ["us_equities", "options"], "sandbox_available": "unknown", "paper_trading_available": "partial"},
}


def build_provider_universe(providers: list[str] | None = None) -> dict:
    selected = providers or list(PROVIDER_METADATA)
    rows = []
    for provider in selected:
        meta = PROVIDER_METADATA.get(provider)
        if not meta:
            continue
        rows.append(
            {
                "provider": provider,
                "region": meta["region"],
                "asset_classes": meta["asset_classes"],
                "sandbox_available": meta["sandbox_available"],
                "paper_trading_available": meta["paper_trading_available"],
                "api_docs_required": True,
                "credential_required": True,
                "market_data_permission_required": True,
                "account_approval_required": True,
                **PROVIDER_BOUNDARY,
            }
        )
    return {"version": "V5.19", "providers": rows, **PROVIDER_BOUNDARY}

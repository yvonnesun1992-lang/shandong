from __future__ import annotations

from provider_selection import PROVIDER_BOUNDARY


MARKET_DATA_REQUIREMENTS = [
    "delayed data allowed",
    "real-time data requirement",
    "exchange entitlement requirement",
    "US equities data",
    "HK equities data",
    "options data",
    "crypto data",
    "quote frequency limit",
    "historical data availability",
    "data redistribution restriction",
    "commercial usage restriction",
]


def build_market_data_permission_checklist(provider: str = "alpaca") -> dict:
    requirements = [{"requirement": item, "confirmed": False} for item in MARKET_DATA_REQUIREMENTS]
    return {"version": "V5.19", "provider": provider, "market_data_ready": False, "requirements": requirements, "blocking_items": MARKET_DATA_REQUIREMENTS, **PROVIDER_BOUNDARY}

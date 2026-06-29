from __future__ import annotations

from provider_selection import PROVIDER_BOUNDARY


ACCOUNT_ITEMS = [
    "account opening status",
    "identity verification status",
    "region eligibility",
    "trading permission request",
    "market data permission request",
    "API access request",
    "paper trading access request",
    "sandbox environment access request",
    "agreement / risk disclosure review",
    "tax / regulatory document review",
    "operations owner assigned",
]


def build_account_preparation_checklist(provider: str = "alpaca") -> dict:
    checklist = [{"item": item, "complete": False, "owner": "future_operator"} for item in ACCOUNT_ITEMS]
    return {"version": "V5.19", "provider": provider, "ready": False, "checklist": checklist, "blocking_items": ACCOUNT_ITEMS, "warnings": [], **PROVIDER_BOUNDARY}

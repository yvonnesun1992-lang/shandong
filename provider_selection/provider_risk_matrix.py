from __future__ import annotations

from provider_selection import PROVIDER_BOUNDARY
from provider_selection.provider_universe import PROVIDER_METADATA


RISK_BASE = {
    "alpaca": (34, "MEDIUM"),
    "ibkr": (46, "MEDIUM"),
    "futu": (55, "MEDIUM"),
    "tiger": (63, "HIGH"),
    "schwab": (61, "HIGH"),
}
RISK_FIELDS = [
    "API stability risk",
    "credential risk",
    "market data entitlement risk",
    "region restriction risk",
    "order routing complexity risk",
    "rate limit risk",
    "documentation ambiguity risk",
    "compliance risk",
    "account approval risk",
    "operational complexity risk",
]


def build_provider_risk_matrix(providers: list[str] | None = None) -> dict:
    selected = providers or list(PROVIDER_METADATA)
    matrix = []
    for provider in selected:
        if provider not in RISK_BASE:
            continue
        score, level = RISK_BASE[provider]
        matrix.append(
            {
                "provider": provider,
                "risk_score": score,
                "risk_level": level,
                "risks": [{"name": field, "level": level} for field in RISK_FIELDS],
                "blocking_items": ["future account approval required", "future credential vault required"],
                **PROVIDER_BOUNDARY,
            }
        )
    return {"version": "V5.19", "matrix": matrix, **PROVIDER_BOUNDARY}

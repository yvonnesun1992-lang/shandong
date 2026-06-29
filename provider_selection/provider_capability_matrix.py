from __future__ import annotations

from provider_selection import PROVIDER_BOUNDARY
from provider_selection.provider_universe import PROVIDER_METADATA


CAPABILITY_BASE = {
    "alpaca": (82, {"paper_trading_support": "high", "sandbox_order_support": "high", "market_data_support": "medium", "equity_support": "high", "options_support": "low", "crypto_support": "medium", "fractional_share_support": "medium", "order_types_supported": "basic", "rate_limit_clarity": "high", "API documentation quality": "high", "region availability": "US", "account opening complexity": "low", "credential isolation fit": "high", "manual approval fit": "high", "kill switch fit": "high", "audit logging fit": "high"}),
    "ibkr": (78, {"paper_trading_support": "high", "sandbox_order_support": "medium", "market_data_support": "high", "equity_support": "high", "options_support": "high", "crypto_support": "low", "fractional_share_support": "low", "order_types_supported": "advanced", "rate_limit_clarity": "medium", "API documentation quality": "medium", "region availability": "global", "account opening complexity": "high", "credential isolation fit": "high", "manual approval fit": "high", "kill switch fit": "high", "audit logging fit": "high"}),
    "futu": (68, {"paper_trading_support": "medium", "sandbox_order_support": "medium", "market_data_support": "medium", "equity_support": "high", "options_support": "medium", "crypto_support": "low", "fractional_share_support": "low", "order_types_supported": "basic", "rate_limit_clarity": "medium", "API documentation quality": "medium", "region availability": "HK/US", "account opening complexity": "medium", "credential isolation fit": "medium", "manual approval fit": "high", "kill switch fit": "medium", "audit logging fit": "medium"}),
    "tiger": (61, {"paper_trading_support": "medium", "sandbox_order_support": "unknown", "market_data_support": "medium", "equity_support": "high", "options_support": "medium", "crypto_support": "low", "fractional_share_support": "low", "order_types_supported": "basic", "rate_limit_clarity": "low", "API documentation quality": "medium", "region availability": "HK/US/SG", "account opening complexity": "medium", "credential isolation fit": "medium", "manual approval fit": "medium", "kill switch fit": "medium", "audit logging fit": "medium"}),
    "schwab": (58, {"paper_trading_support": "medium", "sandbox_order_support": "unknown", "market_data_support": "medium", "equity_support": "high", "options_support": "medium", "crypto_support": "low", "fractional_share_support": "low", "order_types_supported": "basic", "rate_limit_clarity": "low", "API documentation quality": "medium", "region availability": "US", "account opening complexity": "medium", "credential isolation fit": "medium", "manual approval fit": "medium", "kill switch fit": "medium", "audit logging fit": "medium"}),
}


def build_provider_capability_matrix(providers: list[str] | None = None) -> dict:
    selected = providers or list(PROVIDER_METADATA)
    matrix = []
    for provider in selected:
        if provider not in CAPABILITY_BASE:
            continue
        score, capabilities = CAPABILITY_BASE[provider]
        matrix.append({"provider": provider, "capabilities": capabilities, "score": score, "warnings": [], **PROVIDER_BOUNDARY})
    return {"version": "V5.19", "matrix": matrix, **PROVIDER_BOUNDARY}

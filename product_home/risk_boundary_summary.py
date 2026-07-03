from __future__ import annotations

from product_home.init import boundary


def build_risk_boundary_summary() -> dict:
    payload = {
        **boundary(),
        "local_only": True,
        "paper_trading_only": True,
        "safety_status": "OK",
        "disabled_paths": [
            "broker connection",
            "sandbox API",
            "secret read",
            "account read",
            "balance read",
            "position read",
            "order preview",
            "order submission",
            "real money",
        ],
    }
    return payload

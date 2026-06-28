from __future__ import annotations


CAPABILITY_FIELDS = [
    "supports_market_order",
    "supports_limit_order",
    "supports_stop_order",
    "supports_partial_fill",
    "supports_cancel",
    "supports_positions",
    "supports_account",
    "supports_streaming",
]


def build_capability_matrix() -> dict:
    skeleton = {field: False for field in CAPABILITY_FIELDS}
    mock = {field: True for field in CAPABILITY_FIELDS}
    mock["simulation_only"] = True
    return {
        "mock": mock,
        "ibkr_skeleton": {**skeleton, "skeleton_only": True},
        "alpaca_skeleton": {**skeleton, "skeleton_only": True},
        "futu_skeleton": {**skeleton, "skeleton_only": True},
        "tiger_skeleton": {**skeleton, "skeleton_only": True},
        "schwab_skeleton": {**skeleton, "skeleton_only": True},
        "real_connection": False,
        "paper_trading": True,
    }

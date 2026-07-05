from __future__ import annotations

from config.v5_strategy_center_config import get_strategy_center_status


def boundary() -> dict:
    return get_strategy_center_status()

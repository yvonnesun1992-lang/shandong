from __future__ import annotations


def max_position_value(total_capital: float, max_position_pct: float = 0.15) -> float:
    """Maximum money allowed in one stock."""
    return total_capital * max_position_pct


def position_size_by_risk(total_capital: float, entry_price: float, stop_price: float, risk_pct: float = 0.02) -> int:
    """Calculate shares so one trade risks at most 2% of capital."""
    risk_per_share = entry_price - stop_price
    if risk_per_share <= 0:
        return 0

    max_loss = total_capital * risk_pct
    return int(max_loss // risk_per_share)


def suggested_position_size(
    total_capital: float,
    entry_price: float,
    stop_price: float,
    max_position_pct: float = 0.15,
    risk_pct: float = 0.02,
) -> int:
    """Use both max-position and max-risk rules, then choose the smaller size."""
    by_position = int(max_position_value(total_capital, max_position_pct) // entry_price)
    by_risk = position_size_by_risk(total_capital, entry_price, stop_price, risk_pct)
    return max(0, min(by_position, by_risk))

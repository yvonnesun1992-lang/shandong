from __future__ import annotations

import pandas as pd


def _clean_equity_series(equity_series: pd.Series) -> pd.Series:
    equity = pd.to_numeric(equity_series, errors="coerce").dropna()
    if equity.empty:
        raise ValueError("Equity series is empty.")
    if equity.iloc[0] <= 0:
        raise ValueError("Equity series must start with a positive value.")
    return equity


def calculate_max_drawdown(equity_series: pd.Series) -> float:
    """Calculate the largest percentage decline from a previous equity high."""
    equity = _clean_equity_series(equity_series)
    running_high = equity.cummax()
    drawdown = equity / running_high - 1
    return float(drawdown.min())


def calculate_total_return(equity_series: pd.Series) -> float:
    """Calculate total return from the first equity value to the last value."""
    equity = _clean_equity_series(equity_series)
    return float(equity.iloc[-1] / equity.iloc[0] - 1)


def calculate_annualized_return(equity_series: pd.Series, periods_per_year: int = 252) -> float:
    """Annualize a return series by assuming one equity point per period."""
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive.")

    equity = _clean_equity_series(equity_series)
    if len(equity) <= 1:
        return 0.0

    total_return = calculate_total_return(equity)
    return float((1 + total_return) ** (periods_per_year / (len(equity) - 1)) - 1)

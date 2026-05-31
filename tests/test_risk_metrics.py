from __future__ import annotations

import pandas as pd
import pytest

from src.risk.metrics import calculate_annualized_return, calculate_max_drawdown, calculate_total_return


def test_calculate_max_drawdown():
    equity = pd.Series([100, 120, 90, 110])

    result = calculate_max_drawdown(equity)

    assert result == pytest.approx(-0.25)


def test_calculate_total_return():
    equity = pd.Series([100, 125])

    result = calculate_total_return(equity)

    assert result == pytest.approx(0.25)


def test_calculate_annualized_return_runs():
    equity = pd.Series([100, 101, 102, 103])

    result = calculate_annualized_return(equity)

    assert isinstance(result, float)


def test_risk_metrics_reject_empty_data():
    equity = pd.Series([], dtype=float)

    with pytest.raises(ValueError, match="empty"):
        calculate_max_drawdown(equity)

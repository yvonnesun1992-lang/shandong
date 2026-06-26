from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_factor_ic(factor: str, factor_matrix: pd.DataFrame, price_matrix: pd.DataFrame, forward_days: int = 1) -> dict:
    factors = _clean(factor_matrix)
    prices = _clean(price_matrix)
    common_index = factors.index.intersection(prices.index)
    common_columns = factors.columns.intersection(prices.columns)
    factors = factors.loc[common_index, common_columns]
    prices = prices.loc[common_index, common_columns]
    future_returns = prices.shift(-forward_days) / prices - 1

    ic_values = []
    ic_index = []
    valid_index = factors.index[:-forward_days] if forward_days > 0 else factors.index
    for timestamp in valid_index:
        factor_values = factors.loc[timestamp]
        returns = future_returns.loc[timestamp]
        valid = pd.concat([factor_values, returns], axis=1).replace([np.inf, -np.inf], np.nan).dropna()
        if len(valid) < 2 or valid.iloc[:, 0].nunique() <= 1 or valid.iloc[:, 1].nunique() <= 1:
            ic = 0.0
        else:
            ic = float(valid.iloc[:, 0].corr(valid.iloc[:, 1]))
            if not np.isfinite(ic):
                ic = 0.0
        ic_values.append(ic)
        ic_index.append(timestamp)

    ic_series = pd.Series(ic_values, index=pd.DatetimeIndex(ic_index), name=f"{factor}_ic")
    ic_std = float(ic_series.std(ddof=0))
    ic_mean = float(ic_series.mean()) if not ic_series.empty else 0.0
    ic_ir = float(ic_mean / ic_std) if ic_std > 0 else 0.0
    stability = float((ic_series > 0).mean()) if not ic_series.empty else 0.0
    return {
        "factor": factor,
        "ic_series": ic_series,
        "rolling_ic_5": ic_series.rolling(5, min_periods=1).mean(),
        "rolling_ic_10": ic_series.rolling(10, min_periods=1).mean(),
        "rolling_ic_20": ic_series.rolling(20, min_periods=1).mean(),
        "ic_mean": ic_mean,
        "ic_std": ic_std,
        "ic_ir": ic_ir,
        "ic_stability": stability,
    }


def _clean(matrix: pd.DataFrame) -> pd.DataFrame:
    result = matrix.copy()
    result.index = pd.to_datetime(result.index)
    return result.sort_index().apply(pd.to_numeric, errors="coerce")

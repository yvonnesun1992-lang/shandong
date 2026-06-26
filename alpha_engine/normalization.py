from __future__ import annotations

import numpy as np
import pandas as pd


def normalize_factor_matrix(matrix: pd.DataFrame, winsor_limits: tuple[float, float] = (0.01, 0.99)) -> pd.DataFrame:
    frame = matrix.copy().sort_index()
    frame = frame.apply(pd.to_numeric, errors="coerce")
    clipped = frame.apply(lambda row: _winsorize_row(row, winsor_limits), axis=1)
    return clipped.apply(_zscore_row, axis=1)


def _winsorize_row(row: pd.Series, winsor_limits: tuple[float, float]) -> pd.Series:
    valid = row.dropna()
    if valid.empty:
        return row
    lower = valid.quantile(winsor_limits[0])
    upper = valid.quantile(winsor_limits[1])
    return row.clip(lower=lower, upper=upper)


def _zscore_row(row: pd.Series) -> pd.Series:
    valid = row.dropna()
    if valid.empty:
        return row
    std = valid.std(ddof=0)
    if std == 0 or np.isnan(std):
        result = row.copy()
        result.loc[valid.index] = 0.0
        return result
    return (row - valid.mean()) / std

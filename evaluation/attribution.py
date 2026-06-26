from __future__ import annotations

import pandas as pd


def analyze_factor_attribution(factor_returns: pd.DataFrame, factor_weights: dict[str, float]) -> dict:
    frame = factor_returns.copy().sort_index().apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return_contribution = {}
    risk_contribution = {}
    for factor, weight in factor_weights.items():
        if factor not in frame:
            continue
        series = frame[factor]
        return_contribution[factor] = float(series.mean() * weight)
        risk_contribution[factor] = float(series.std(ddof=0) * abs(weight))
    return {
        "return_contribution": return_contribution,
        "risk_contribution": risk_contribution,
        "correlation_matrix": frame.corr(),
    }

from __future__ import annotations

import math

import pandas as pd


class MultiFactorPortfolio:
    def __init__(self, max_weight_per_asset: float = 0.10) -> None:
        self.max_weight_per_asset = max_weight_per_asset

    def construct(self, alpha_scores: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for _, row in alpha_scores.sort_index().iterrows():
            weights = self._construct_row(row.astype(float))
            rows.append(weights)
        result = pd.DataFrame(rows, index=alpha_scores.sort_index().index).fillna(0.0)
        return result.reindex(columns=alpha_scores.columns, fill_value=0.0)

    def _construct_row(self, scores: pd.Series) -> pd.Series:
        clean = scores.dropna().sort_values(ascending=False)
        if clean.empty:
            return pd.Series(0.0, index=scores.index)
        min_assets = max(1, math.ceil(1.0 / self.max_weight_per_asset))
        eligible = clean[clean > 0]
        if len(eligible) < min_assets:
            eligible = clean.head(min(min_assets, len(clean)))
        positive = eligible - eligible.min() + 1e-6
        weights = positive / positive.sum()
        weights = _cap_and_redistribute(weights, self.max_weight_per_asset, len(scores.index))
        result = pd.Series(0.0, index=scores.index)
        result.loc[weights.index] = weights
        return result


def _cap_and_redistribute(weights: pd.Series, cap: float, total_assets: int) -> pd.Series:
    if total_assets * cap < 1.0:
        raise ValueError("Infeasible cap for the available asset universe")
    remaining = weights.copy()
    fixed = pd.Series(dtype=float)
    target_total = 1.0

    while not remaining.empty:
        normalized = remaining / (remaining.sum() or 1.0) * (target_total - fixed.sum())
        over = normalized[normalized > cap]
        if over.empty:
            fixed = pd.concat([fixed, normalized])
            break
        fixed = pd.concat([fixed, pd.Series(cap, index=over.index)])
        remaining = remaining.drop(index=over.index)
        if fixed.sum() >= target_total:
            break

    fixed = fixed.groupby(level=0).sum()
    total = fixed.sum() or 1.0
    return fixed / total

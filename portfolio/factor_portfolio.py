from __future__ import annotations

import numpy as np
import pandas as pd


class FactorPortfolioSimulator:
    def simulate(
        self,
        factor_matrices: dict[str, pd.DataFrame],
        price_matrix: pd.DataFrame,
        factor_scores: dict[str, float],
        forward_days: int = 1,
    ) -> dict:
        factor_weights = self._normalize_scores(factor_scores)
        combined = self._combine_factors(factor_matrices, factor_weights)
        prices = price_matrix.sort_index().apply(pd.to_numeric, errors="coerce").ffill()
        asset_returns = prices.pct_change(periods=forward_days)
        shifted_scores = combined.shift(forward_days)
        portfolio_returns = []
        timestamps = []

        common_index = shifted_scores.index.intersection(asset_returns.index)
        for timestamp in common_index:
            scores = shifted_scores.loc[timestamp].replace([np.inf, -np.inf], np.nan).dropna()
            returns = asset_returns.loc[timestamp].reindex(scores.index).dropna()
            scores = scores.reindex(returns.index)
            if returns.empty or scores.empty:
                continue
            if scores.abs().sum() == 0:
                portfolio_return = 0.0
            else:
                asset_weights = scores.clip(lower=0)
                if asset_weights.sum() == 0:
                    asset_weights = scores.rank(pct=True).clip(lower=0)
                asset_weights = asset_weights / (asset_weights.sum() or 1.0)
                portfolio_return = float((asset_weights * returns).sum())
            portfolio_returns.append(portfolio_return)
            timestamps.append(timestamp)

        returns_series = pd.Series(portfolio_returns, index=pd.DatetimeIndex(timestamps), name="factor_portfolio_return")
        cumulative_return = float((1 + returns_series.fillna(0)).prod() - 1)
        return {
            "factor_weights": factor_weights,
            "portfolio_returns": returns_series,
            "cumulative_returns": (1 + returns_series.fillna(0)).cumprod() - 1,
            "cumulative_return": cumulative_return,
        }

    @staticmethod
    def _normalize_scores(scores: dict[str, float]) -> dict[str, float]:
        positive = {factor: max(float(score or 0.0), 0.0) for factor, score in scores.items()}
        total = sum(positive.values())
        if total <= 0:
            count = len(positive) or 1
            return {factor: 1.0 / count for factor in positive}
        return {factor: value / total for factor, value in positive.items() if value > 0}

    @staticmethod
    def _combine_factors(factor_matrices: dict[str, pd.DataFrame], factor_weights: dict[str, float]) -> pd.DataFrame:
        combined = None
        for factor, weight in factor_weights.items():
            matrix = factor_matrices[factor].sort_index().apply(pd.to_numeric, errors="coerce")
            zscored = matrix.sub(matrix.mean(axis=1), axis=0).div(matrix.std(axis=1, ddof=0).replace(0, np.nan), axis=0).fillna(0)
            weighted = zscored * weight
            combined = weighted if combined is None else combined.add(weighted, fill_value=0)
        return combined.fillna(0) if combined is not None else pd.DataFrame()

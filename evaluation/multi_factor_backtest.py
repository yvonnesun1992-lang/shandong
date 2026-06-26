from __future__ import annotations

import math

import numpy as np
import pandas as pd


class MultiFactorBacktest:
    def __init__(self, transaction_cost_bps: float = 0.0, slippage_bps: float = 0.0) -> None:
        self.transaction_cost_bps = float(transaction_cost_bps)
        self.slippage_bps = float(slippage_bps)

    def run(self, portfolio_weights: pd.DataFrame, price_matrix: pd.DataFrame, regime: dict | None = None) -> dict:
        weights = portfolio_weights.sort_index().apply(pd.to_numeric, errors="coerce").fillna(0.0)
        prices = price_matrix.sort_index().apply(pd.to_numeric, errors="coerce").ffill()
        asset_returns = prices.pct_change()
        shifted_weights = weights.shift(1)

        common_index = shifted_weights.index.intersection(asset_returns.index)
        aligned_weights = []
        portfolio_returns = []
        gross_returns = []
        costs = []
        timestamps = []
        for timestamp in common_index:
            row_weights = shifted_weights.loc[timestamp].dropna()
            row_returns = asset_returns.loc[timestamp].reindex(row_weights.index).dropna()
            row_weights = row_weights.reindex(row_returns.index).fillna(0.0)
            if row_weights.empty or row_returns.empty or row_weights.sum() <= 0:
                continue
            gross_return = float((row_weights * row_returns).sum())
            turnover = _row_turnover(row_weights, aligned_weights[-1] if aligned_weights else None)
            cost = turnover * (self.transaction_cost_bps + self.slippage_bps) / 10_000
            gross_returns.append(gross_return)
            costs.append(cost)
            portfolio_returns.append(gross_return - cost)
            aligned_weights.append(row_weights)
            timestamps.append(timestamp)

        returns = pd.Series(portfolio_returns, index=pd.DatetimeIndex(timestamps), name="portfolio_return")
        gross = pd.Series(gross_returns, index=pd.DatetimeIndex(timestamps), name="gross_portfolio_return")
        cost_series = pd.Series(costs, index=pd.DatetimeIndex(timestamps), name="trading_cost")
        aligned_weight_frame = pd.DataFrame(aligned_weights, index=pd.DatetimeIndex(timestamps)).fillna(0.0) if timestamps else shifted_weights.iloc[0:0]
        equity = (1 + returns.fillna(0.0)).cumprod()
        return {
            "portfolio_returns": returns,
            "gross_portfolio_returns": gross,
            "costs": cost_series,
            "equity_curve": pd.DataFrame({"datetime": equity.index, "equity": equity.values}),
            "metrics": _calculate_metrics(returns, aligned_weight_frame, gross, cost_series),
            "regime": regime or {"state": "unknown", "confidence": 0.0},
        }


def _calculate_metrics(returns: pd.Series, weights: pd.DataFrame, gross_returns: pd.Series | None = None, costs: pd.Series | None = None) -> dict:
    if returns.empty:
        return {
            "total_return": 0.0,
            "gross_total_return": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "calmar_ratio": 0.0,
            "turnover": 0.0,
            "total_cost": 0.0,
        }
    equity = (1 + returns.fillna(0.0)).cumprod()
    total_return = float(equity.iloc[-1] - 1.0)
    gross_equity = (1 + (gross_returns if gross_returns is not None else returns).fillna(0.0)).cumprod()
    gross_total_return = float(gross_equity.iloc[-1] - 1.0)
    std = float(returns.std(ddof=0))
    downside = returns[returns < 0]
    downside_std = float(downside.std(ddof=0))
    sharpe = float(returns.mean() / std * math.sqrt(252)) if std > 0 else 0.0
    sortino = float(returns.mean() / downside_std * math.sqrt(252)) if downside_std > 0 else 0.0
    peak = equity.cummax()
    drawdown = ((peak - equity) / peak.replace(0, np.nan)).fillna(0.0)
    max_drawdown = float(drawdown.max())
    annual_return = float((1 + total_return) ** (252 / max(len(returns), 1)) - 1) if total_return > -1 else -1.0
    calmar = float(annual_return / max_drawdown) if max_drawdown > 0 else 0.0
    turnover = float(weights.diff().abs().sum(axis=1).fillna(0.0).mean()) if not weights.empty else 0.0
    total_cost = float(costs.fillna(0.0).sum()) if costs is not None else 0.0
    return {
        "total_return": total_return,
        "gross_total_return": gross_total_return,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": max_drawdown,
        "calmar_ratio": calmar,
        "turnover": turnover,
        "total_cost": total_cost,
    }


def _row_turnover(current: pd.Series, previous: pd.Series | None) -> float:
    if previous is None:
        return float(current.abs().sum())
    aligned = pd.concat([current, previous], axis=1).fillna(0.0)
    return float((aligned.iloc[:, 0] - aligned.iloc[:, 1]).abs().sum())

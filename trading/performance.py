from __future__ import annotations

import math

import pandas as pd


def calculate_performance_metrics(equity_curve: list[dict], trade_history: list[dict], initial_cash: float) -> dict:
    if not equity_curve:
        return _empty_metrics()
    equity = pd.Series([float(item["equity"]) for item in equity_curve])
    returns = equity.pct_change().dropna()
    total_return = float(equity.iloc[-1] / float(initial_cash) - 1.0) if initial_cash else 0.0
    annual_return = float((1 + total_return) ** (252 / max(len(equity), 1)) - 1) if total_return > -1 else -1.0
    std = float(returns.std(ddof=0))
    sharpe = float(returns.mean() / std * math.sqrt(252)) if std > 0 else 0.0
    peak = equity.cummax()
    max_drawdown = float(((peak - equity) / peak.replace(0, pd.NA)).fillna(0.0).max())
    wins = 0
    sells = [trade for trade in trade_history if trade.get("side") == "SELL"]
    for trade in sells:
        if float(trade.get("cash_effect", 0.0)) > 0:
            wins += 1
    number_of_trades = len(trade_history)
    return {
        "total_return": total_return,
        "annual_return": annual_return,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe,
        "win_rate": float(wins / len(sells)) if sells else 0.0,
        "number_of_trades": number_of_trades,
        "average_trade_return": float(sum(float(t.get("cash_effect", 0.0)) for t in trade_history) / number_of_trades) if number_of_trades else 0.0,
        "total_fees": float(sum(float(t.get("fee", 0.0)) for t in trade_history)),
        "total_slippage_cost": float(sum(float(t.get("slippage_cost", 0.0)) for t in trade_history)),
    }


def _empty_metrics() -> dict:
    return {
        "total_return": 0.0,
        "annual_return": 0.0,
        "max_drawdown": 0.0,
        "sharpe_ratio": 0.0,
        "win_rate": 0.0,
        "number_of_trades": 0,
        "average_trade_return": 0.0,
        "total_fees": 0.0,
        "total_slippage_cost": 0.0,
    }

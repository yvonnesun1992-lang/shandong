from __future__ import annotations

"""
Simple V1 backtest module.

This module keeps the backtest beginner-friendly and avoids real trading.
"""

import pandas as pd

from src.strategies.trend_score import add_trend_scores


def calculate_max_drawdown(equity: pd.Series) -> float:
    """Maximum fall from a previous high point."""
    running_high = equity.cummax()
    drawdown = equity / running_high - 1
    return float(drawdown.min())


def run_simple_backtest(data: pd.DataFrame, initial_cash: float = 100_000) -> dict:
    """Run one-stock V1 backtest with simple buy and sell rules."""
    scored = add_trend_scores(data)
    if scored.empty:
        raise ValueError("Not enough data for backtest. Need at least 120 rows.")

    cash = initial_cash
    max_position_cash = initial_cash * 0.15
    shares = 0
    entry_price = 0.0
    trades: list[dict] = []
    equity_curve = []

    for _, row in scored.iterrows():
        close = float(row["close"])
        score = int(row["trend_score"])
        should_buy = shares == 0 and score >= 80
        should_sell = shares > 0 and (score < 60 or close < float(row["ma60"]))

        if should_buy:
            # V1 only uses up to 15% of initial cash for one stock.
            buy_cash = min(cash, max_position_cash)
            shares = int(buy_cash // close)
            if shares > 0:
                entry_price = close
                cash -= shares * close

        elif should_sell:
            cash += shares * close
            trades.append({"entry": entry_price, "exit": close, "return": close / entry_price - 1})
            shares = 0
            entry_price = 0.0

        equity_curve.append(cash + shares * close)

    if shares > 0:
        final_close = float(scored.iloc[-1]["close"])
        cash += shares * final_close
        trades.append({"entry": entry_price, "exit": final_close, "return": final_close / entry_price - 1})
        shares = 0

    equity = pd.Series(equity_curve, index=scored["date"])
    final_value = float(cash)
    total_return = final_value / initial_cash - 1
    days = max((scored["date"].iloc[-1] - scored["date"].iloc[0]).days, 1)
    annualized_return = (1 + total_return) ** (365 / days) - 1
    win_rate = sum(1 for trade in trades if trade["return"] > 0) / len(trades) if trades else 0.0

    return {
        "total_return": float(total_return),
        "annualized_return": float(annualized_return),
        "max_drawdown": calculate_max_drawdown(equity),
        "win_rate": float(win_rate),
        "number_of_trades": len(trades),
        "final_portfolio_value": final_value,
    }

from __future__ import annotations

import pandas as pd

from src.risk.metrics import calculate_annualized_return, calculate_max_drawdown, calculate_total_return
from src.strategies.trend_score import add_trend_scores


REQUIRED_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def _prepare_symbol_data(symbol: str, data: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"{symbol} missing OHLCV columns: {missing}")

    result = data[REQUIRED_COLUMNS].copy()
    result["date"] = pd.to_datetime(result["date"])
    numeric_columns = ["open", "high", "low", "close", "volume"]
    result[numeric_columns] = result[numeric_columns].apply(pd.to_numeric, errors="coerce")
    result = result.dropna(subset=REQUIRED_COLUMNS).sort_values("date").reset_index(drop=True)
    if len(result) < 120:
        return pd.DataFrame()
    return add_trend_scores(result)


def _is_rebalance_date(date: pd.Timestamp, previous_date: pd.Timestamp | None, frequency: str) -> bool:
    if previous_date is None:
        return True
    frequency = frequency.lower()
    if frequency == "daily":
        return True
    if frequency == "weekly":
        return date.isocalendar().week != previous_date.isocalendar().week or date.year != previous_date.year
    if frequency == "monthly":
        return date.month != previous_date.month or date.year != previous_date.year
    raise ValueError("rebalance_frequency must be 'daily', 'weekly', or 'monthly'.")


def _latest_rows_by_date(scored_data: dict[str, pd.DataFrame], current_date: pd.Timestamp) -> dict[str, pd.Series]:
    rows = {}
    for symbol, data in scored_data.items():
        available = data[data["date"] <= current_date]
        if not available.empty:
            rows[symbol] = available.iloc[-1]
    return rows


def _positions_value(positions: dict[str, int], rows: dict[str, pd.Series]) -> float:
    value = 0.0
    for symbol, quantity in positions.items():
        if symbol in rows:
            value += quantity * float(rows[symbol]["close"])
    return float(value)


def run_portfolio_backtest(
    price_data: dict[str, pd.DataFrame],
    initial_cash: float = 100000.0,
    max_position_pct: float = 0.15,
    rebalance_frequency: str = "monthly",
    min_score_to_buy: int = 80,
    min_score_to_hold: int = 60,
) -> dict:
    """Run a simple multi-stock trend-following portfolio backtest."""
    if initial_cash <= 0:
        raise ValueError("initial_cash must be positive.")
    if not 0 < max_position_pct <= 1:
        raise ValueError("max_position_pct must be greater than 0 and less than or equal to 1.")
    if not price_data:
        raise ValueError("price_data must contain at least one symbol.")

    scored_data: dict[str, pd.DataFrame] = {}
    skipped_symbols: list[str] = []
    for symbol, data in price_data.items():
        prepared = _prepare_symbol_data(symbol, data)
        if prepared.empty:
            skipped_symbols.append(symbol)
        else:
            scored_data[symbol] = prepared

    if not scored_data:
        raise ValueError("No symbols have enough data for portfolio backtest.")

    all_dates = sorted(set(pd.concat([data["date"] for data in scored_data.values()]).dropna()))
    cash = float(initial_cash)
    positions: dict[str, int] = {}
    trades: list[dict] = []
    equity_rows: list[dict] = []
    previous_date: pd.Timestamp | None = None

    for current_date in all_dates:
        rows = _latest_rows_by_date(scored_data, current_date)
        if not rows:
            continue

        for symbol in list(positions):
            row = rows.get(symbol)
            if row is None:
                continue
            close = float(row["close"])
            score = int(row["trend_score"])
            if score < min_score_to_hold or close < float(row["ma60"]):
                quantity = positions.pop(symbol)
                amount = quantity * close
                cash += amount
                trades.append(
                    {
                        "date": current_date,
                        "symbol": symbol,
                        "action": "SELL",
                        "price": close,
                        "quantity": quantity,
                        "amount": amount,
                        "score": score,
                    }
                )

        positions_value = _positions_value(positions, rows)
        total_value = cash + positions_value

        if _is_rebalance_date(current_date, previous_date, rebalance_frequency):
            candidates = sorted(
                (
                    (symbol, row)
                    for symbol, row in rows.items()
                    if int(row["trend_score"]) >= min_score_to_buy and symbol not in positions
                ),
                key=lambda item: int(item[1]["trend_score"]),
                reverse=True,
            )
            for symbol, row in candidates:
                close = float(row["close"])
                score = int(row["trend_score"])
                max_position_value = total_value * max_position_pct
                quantity = int(min(cash, max_position_value) // close)
                if quantity <= 0:
                    continue
                amount = quantity * close
                if amount > cash:
                    continue
                cash -= amount
                positions[symbol] = positions.get(symbol, 0) + quantity
                trades.append(
                    {
                        "date": current_date,
                        "symbol": symbol,
                        "action": "BUY",
                        "price": close,
                        "quantity": quantity,
                        "amount": amount,
                        "score": score,
                    }
                )

        positions_value = _positions_value(positions, rows)
        total_value = cash + positions_value
        if cash < -0.000001:
            raise ValueError("Backtest generated negative cash.")
        if any(quantity < 0 for quantity in positions.values()):
            raise ValueError("Backtest generated negative positions.")

        equity_rows.append(
            {
                "date": current_date,
                "cash": float(cash),
                "positions_value": float(positions_value),
                "total_value": float(total_value),
            }
        )
        previous_date = current_date

    equity_curve = pd.DataFrame(equity_rows)
    if equity_curve.empty:
        raise ValueError("Portfolio backtest produced no equity curve.")

    trades_table = pd.DataFrame(trades, columns=["date", "symbol", "action", "price", "quantity", "amount", "score"])
    final_cash = float(equity_curve.iloc[-1]["cash"])
    final_positions_value = float(equity_curve.iloc[-1]["positions_value"])
    summary = {
        "total_return": calculate_total_return(equity_curve["total_value"]),
        "annualized_return": calculate_annualized_return(equity_curve["total_value"]),
        "max_drawdown": calculate_max_drawdown(equity_curve["total_value"]),
        "number_of_trades": int(len(trades_table)),
        "final_portfolio_value": float(equity_curve.iloc[-1]["total_value"]),
        "cash": final_cash,
        "positions_value": final_positions_value,
        "skipped_symbols": skipped_symbols,
    }

    return {
        "equity_curve": equity_curve,
        "trades": trades_table,
        "summary": summary,
        "skipped_symbols": skipped_symbols,
    }

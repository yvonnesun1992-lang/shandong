from __future__ import annotations

import pandas as pd
import yfinance as yf


STANDARD_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def get_us_ohlcv(symbol: str, period: str = "2y") -> pd.DataFrame:
    """Download US stock data and return a standard OHLCV table."""
    data = yf.download(symbol, period=period, auto_adjust=False, progress=False)
    if data.empty:
        raise ValueError(f"No US data found for symbol: {symbol}")

    data = data.reset_index()
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [column[0] for column in data.columns]

    result = data.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    result = result[STANDARD_COLUMNS].copy()
    result["date"] = pd.to_datetime(result["date"])
    return result.dropna().sort_values("date").reset_index(drop=True)

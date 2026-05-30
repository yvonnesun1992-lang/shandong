from __future__ import annotations

import pandas as pd
import yfinance as yf

from src.data.sample_data import load_sample_ohlcv


STANDARD_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def _fallback_us_sample(error: Exception) -> pd.DataFrame:
    data = load_sample_ohlcv("us", "NVDA")
    data.attrs["fallback_reason"] = str(error)
    return data


def _validate_ohlcv(data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    missing = [column for column in STANDARD_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"US data for {symbol} missing columns: {missing}")

    result = data[STANDARD_COLUMNS].copy()
    result["date"] = pd.to_datetime(result["date"])
    numeric_columns = ["open", "high", "low", "close", "volume"]
    result[numeric_columns] = result[numeric_columns].apply(pd.to_numeric, errors="coerce")
    result = result.dropna().sort_values("date").reset_index(drop=True)
    if result.empty:
        raise ValueError(f"No valid US OHLCV rows found for symbol: {symbol}")

    result.attrs["is_sample_data"] = False
    result.attrs["data_source"] = "yfinance"
    return result


def get_us_ohlcv(symbol: str, period: str = "2y", use_sample_fallback: bool = True) -> pd.DataFrame:
    """Download US stock data and return a standard OHLCV table."""
    try:
        data = yf.download(symbol, period=period, auto_adjust=False, progress=False, timeout=5)
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
        return _validate_ohlcv(result, symbol)
    except Exception as error:
        if use_sample_fallback:
            return _fallback_us_sample(error)
        raise

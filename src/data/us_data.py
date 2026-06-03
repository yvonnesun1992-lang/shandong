from __future__ import annotations

import pandas as pd
import yfinance as yf

from src.data.price_cache import cache_price_data, has_cached_price_data, load_cached_price_data
from src.data.sample_data import load_sample_ohlcv


STANDARD_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def _fallback_us_sample(error: Exception) -> pd.DataFrame:
    data = load_sample_ohlcv("us", "NVDA")
    data.attrs["fallback_reason"] = str(error)
    data.attrs["market"] = "us"
    data.attrs["symbol"] = "NVDA"
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
    result.attrs["data_source"] = "remote"
    result.attrs["market"] = "us"
    result.attrs["symbol"] = symbol.strip().upper()
    return result


def get_us_ohlcv(
    symbol: str,
    period: str = "2y",
    use_sample_fallback: bool = True,
    use_cache: bool = True,
    refresh_cache: bool = False,
) -> pd.DataFrame:
    """Download US stock data and return a standard OHLCV table."""
    clean_symbol = symbol.strip().upper()
    if use_cache and not refresh_cache and has_cached_price_data("us", clean_symbol):
        return load_cached_price_data("us", clean_symbol)

    try:
        data = yf.download(clean_symbol, period=period, auto_adjust=False, progress=False, timeout=5)
        if data.empty:
            raise ValueError(f"No US data found for symbol: {clean_symbol}")

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
        result = _validate_ohlcv(result, clean_symbol)
        if use_cache:
            cache_price_data("us", clean_symbol, result)
        return result
    except Exception as error:
        if use_sample_fallback:
            return _fallback_us_sample(error)
        raise

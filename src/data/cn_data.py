from __future__ import annotations

import pandas as pd
import akshare as ak

from src.data.sample_data import load_sample_ohlcv


STANDARD_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def _fallback_cn_sample(error: Exception) -> pd.DataFrame:
    data = load_sample_ohlcv("cn", "300308")
    data.attrs["fallback_reason"] = str(error)
    return data


def _validate_ohlcv(data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    missing = [column for column in STANDARD_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"A-share data for {symbol} missing columns: {missing}")

    result = data[STANDARD_COLUMNS].copy()
    result["date"] = pd.to_datetime(result["date"])
    numeric_columns = ["open", "high", "low", "close", "volume"]
    result[numeric_columns] = result[numeric_columns].apply(pd.to_numeric, errors="coerce")
    result = result.dropna().sort_values("date").reset_index(drop=True)
    if result.empty:
        raise ValueError(f"No valid A-share OHLCV rows found for symbol: {symbol}")

    result.attrs["is_sample_data"] = False
    result.attrs["data_source"] = "akshare"
    return result


def get_cn_ohlcv(symbol: str, start_date: str = "20220101", use_sample_fallback: bool = True) -> pd.DataFrame:
    """Download A-share data and return a standard OHLCV table."""
    try:
        data = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            adjust="qfq",
        )
        if data.empty:
            raise ValueError(f"No A-share data found for symbol: {symbol}")

        result = data.rename(
            columns={
                "日期": "date",
                "开盘": "open",
                "最高": "high",
                "最低": "low",
                "收盘": "close",
                "成交量": "volume",
            }
        )
        return _validate_ohlcv(result, symbol)
    except Exception as error:
        if use_sample_fallback:
            return _fallback_cn_sample(error)
        raise

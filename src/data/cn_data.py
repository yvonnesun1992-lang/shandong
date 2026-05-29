from __future__ import annotations

import pandas as pd
import akshare as ak


STANDARD_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def get_cn_ohlcv(symbol: str, start_date: str = "20220101") -> pd.DataFrame:
    """Download A-share data and return a standard OHLCV table."""
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
    result = result[STANDARD_COLUMNS].copy()
    result["date"] = pd.to_datetime(result["date"])
    return result.dropna().sort_values("date").reset_index(drop=True)

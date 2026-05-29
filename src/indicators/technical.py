from __future__ import annotations

import pandas as pd


def moving_average(series: pd.Series, window: int) -> pd.Series:
    """Calculate a simple moving average."""
    return series.rolling(window=window, min_periods=window).mean()


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Calculate RSI with the common 14-day default."""
    change = series.diff()
    gain = change.clip(lower=0)
    loss = -change.clip(upper=0)

    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    relative_strength = avg_gain / avg_loss.replace(0, pd.NA)
    result = 100 - (100 / (1 + relative_strength))

    # If price only rises during the window, RSI should be 100.
    result = result.where(avg_loss != 0, 100)
    return result.fillna(0)


def add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Add V1 indicators used by the trend score strategy."""
    result = data.copy()
    result["ma20"] = moving_average(result["close"], 20)
    result["ma60"] = moving_average(result["close"], 60)
    result["ma120"] = moving_average(result["close"], 120)
    result["rsi14"] = rsi(result["close"], 14)
    result["volume_ma20"] = moving_average(result["volume"], 20)
    return result

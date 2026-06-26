from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_factors(data: pd.DataFrame) -> pd.DataFrame:
    frame = _prepare(data)
    close = frame["close"]
    returns = close.pct_change().replace([np.inf, -np.inf], np.nan)

    frame["momentum_5d"] = close.pct_change(5)
    frame["momentum_10d"] = close.pct_change(10)
    frame["momentum_20d"] = close.pct_change(20)
    frame["momentum_60d"] = close.pct_change(60)

    ma20 = close.rolling(20, min_periods=2).mean()
    std20 = close.rolling(20, min_periods=2).std(ddof=0).replace(0, np.nan)
    ma60 = close.rolling(60, min_periods=2).mean()
    frame["zscore_price"] = ((close - ma20) / std20).replace([np.inf, -np.inf], np.nan)
    frame["distance_to_ma"] = ((close - ma20) / ma20.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
    frame["price_distance_ma20"] = frame["distance_to_ma"]
    lower = ma20 - 2 * std20
    upper = ma20 + 2 * std20
    frame["bollinger_position"] = ((close - lower) / (upper - lower).replace(0, np.nan)).clip(0, 1)

    frame["realized_vol_5d"] = returns.rolling(5, min_periods=2).std(ddof=0) * np.sqrt(252)
    frame["realized_vol_20d"] = returns.rolling(20, min_periods=2).std(ddof=0) * np.sqrt(252)
    frame["volatility_change"] = frame["realized_vol_5d"] - frame["realized_vol_20d"]
    vol_median = frame["realized_vol_20d"].rolling(60, min_periods=5).median()
    frame["volatility_regime"] = np.where(frame["realized_vol_20d"] > vol_median, 1.0, 0.0)

    frame["ma_slope"] = ma20.diff(5) / ma20.shift(5).replace(0, np.nan)
    frame["ma_slope_20"] = ma20.diff(20) / ma20.shift(20).replace(0, np.nan)
    frame["trend_strength"] = ((ma20 - ma60).abs() / close.replace(0, np.nan)).clip(0, 1)
    rolling_high = frame["high"].rolling(20, min_periods=2).max()
    rolling_low = frame["low"].rolling(20, min_periods=2).min()
    frame["breakout_strength"] = ((close - rolling_low) / (rolling_high - rolling_low).replace(0, np.nan)).clip(0, 1)
    high_low = (frame["high"] - frame["low"]).abs()
    directional = close.diff().abs()
    frame["adx_proxy"] = (directional.rolling(14, min_periods=2).mean() / high_low.rolling(14, min_periods=2).mean().replace(0, np.nan)).clip(0, 1)

    factor_cols = [
        "momentum_5d",
        "momentum_10d",
        "momentum_20d",
        "momentum_60d",
        "zscore_price",
        "distance_to_ma",
        "price_distance_ma20",
        "bollinger_position",
        "realized_vol_5d",
        "realized_vol_20d",
        "volatility_change",
        "volatility_regime",
        "ma_slope",
        "ma_slope_20",
        "trend_strength",
        "breakout_strength",
        "adx_proxy",
    ]
    frame[factor_cols] = frame[factor_cols].replace([np.inf, -np.inf], np.nan)
    return frame


def _prepare(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.sort_values("datetime").reset_index(drop=True)
    frame[["open", "high", "low", "close"]] = frame[["open", "high", "low", "close"]].ffill()
    frame["volume"] = frame["volume"].ffill().fillna(0)
    return frame.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)

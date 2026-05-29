from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.indicators.technical import add_technical_indicators


US_WATCHLIST = ["NVDA", "AMD", "PLTR", "TSLA", "MSFT", "GOOGL", "META", "AVGO", "CORZ"]
CN_WATCHLIST = ["300308", "300502", "601138", "002371", "603986", "000977", "002463", "300476", "688256"]


@dataclass(frozen=True)
class TrendScore:
    symbol: str
    score: int
    status: str
    close: float
    rsi14: float


def score_status(score: int) -> str:
    if score >= 80:
        return "Strong trend"
    if score >= 60:
        return "Watchlist"
    if score >= 40:
        return "Neutral"
    return "Weak"


def calculate_trend_score(row: pd.Series) -> int:
    """Calculate a 0 to 100 score from one row with indicators."""
    score = 0
    if row["close"] > row["ma20"]:
        score += 15
    if row["close"] > row["ma60"]:
        score += 20
    if row["close"] > row["ma120"]:
        score += 20
    if row["ma20"] > row["ma60"]:
        score += 15
    if row["ma60"] > row["ma120"]:
        score += 15
    if 50 <= row["rsi14"] <= 75:
        score += 10
    if row["volume"] > row["volume_ma20"]:
        score += 5
    return min(score, 100)


def add_trend_scores(data: pd.DataFrame) -> pd.DataFrame:
    """Add indicators, score, and status columns to a price table."""
    result = add_technical_indicators(data)
    needed = ["ma20", "ma60", "ma120", "rsi14", "volume_ma20"]
    result = result.dropna(subset=needed).copy()
    result["trend_score"] = result.apply(calculate_trend_score, axis=1)
    result["trend_status"] = result["trend_score"].apply(score_status)
    return result


def latest_trend_score(symbol: str, data: pd.DataFrame) -> TrendScore:
    scored = add_trend_scores(data)
    if scored.empty:
        raise ValueError(f"Not enough data to calculate trend score for {symbol}")
    latest = scored.iloc[-1]
    return TrendScore(
        symbol=symbol,
        score=int(latest["trend_score"]),
        status=str(latest["trend_status"]),
        close=float(latest["close"]),
        rsi14=float(latest["rsi14"]),
    )

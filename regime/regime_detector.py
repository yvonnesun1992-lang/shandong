from __future__ import annotations

import pandas as pd

from feature_engine.factors import calculate_factors


class RegimeDetector:
    def __init__(self, low_volatility_threshold: float = 0.25, high_volatility_threshold: float = 0.45, trend_threshold: float = 0.03) -> None:
        self.low_volatility_threshold = low_volatility_threshold
        self.high_volatility_threshold = high_volatility_threshold
        self.trend_threshold = trend_threshold

    def detect(self, data: pd.DataFrame) -> dict:
        factors = calculate_factors(data)
        latest = factors.iloc[-1]
        momentum = float(latest["momentum_20d"])
        volatility = float(latest["realized_vol_20d"])
        trend_strength = float(latest["trend_strength"])
        zscore = abs(float(latest["zscore_price"]))
        close = factors["close"]
        peak = close.cummax()
        drawdown = ((peak - close) / peak.replace(0, pd.NA)).fillna(0)
        drawdown_increasing = len(drawdown) > 5 and drawdown.iloc[-1] > drawdown.iloc[-5]

        bull_score = 0
        bull_score += 1 if momentum > 0 else 0
        bull_score += 1 if volatility <= self.low_volatility_threshold or volatility <= factors["realized_vol_20d"].median() else 0
        bull_score += 1 if trend_strength >= self.trend_threshold else 0

        bear_score = 0
        bear_score += 1 if momentum < 0 else 0
        bear_score += 1 if volatility >= self.high_volatility_threshold or volatility >= factors["realized_vol_20d"].quantile(0.7) else 0
        bear_score += 1 if drawdown_increasing else 0

        sideways_score = 0
        sideways_score += 1 if trend_strength < self.trend_threshold else 0
        sideways_score += 1 if zscore >= 0.5 or abs(momentum) < 0.03 else 0
        sideways_score += 1 if volatility < self.high_volatility_threshold else 0

        scores = {"bull": bull_score, "bear": bear_score, "sideways": sideways_score}
        state = max(scores, key=scores.get)
        confidence = min(scores[state] / 3, 1.0)
        return {"state": state, "confidence": float(confidence)}

from __future__ import annotations

import pandas as pd


class MomentumStrategy:
    def __init__(self, lookback: int = 20, threshold: float = 0.05) -> None:
        if lookback <= 0:
            raise ValueError("lookback must be positive")
        self.lookback = lookback
        self.threshold = threshold

    def generate_signal(self, data: pd.DataFrame, symbol: str) -> dict:
        frame = data.copy().sort_values("datetime").reset_index(drop=True)
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce").ffill().bfill()
        if len(frame) <= self.lookback:
            return _signal(symbol, "HOLD", 0.0, frame)

        previous = frame["close"].iloc[-self.lookback - 1]
        current = frame["close"].iloc[-1]
        if previous == 0 or pd.isna(previous) or pd.isna(current):
            return _signal(symbol, "HOLD", 0.0, frame)

        momentum = float((current - previous) / previous)
        strength = min(abs(momentum) / max(self.threshold, 1e-12), 1.0)
        if momentum > self.threshold:
            return _signal(symbol, "BUY", strength, frame)
        if momentum < -self.threshold:
            return _signal(symbol, "SELL", strength, frame)
        return _signal(symbol, "HOLD", 0.0, frame)


def _signal(symbol: str, action: str, strength: float, frame: pd.DataFrame) -> dict:
    timestamp = pd.to_datetime(frame["datetime"]).iloc[-1] if not frame.empty else pd.Timestamp.utcnow()
    return {"symbol": symbol, "action": action, "strength": float(max(0.0, min(strength, 1.0))), "timestamp": timestamp}

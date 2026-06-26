from __future__ import annotations

import pandas as pd


class MeanReversionStrategy:
    def __init__(self, window: int = 20, num_std: float = 2.0) -> None:
        if window <= 1:
            raise ValueError("window must be greater than 1")
        self.window = window
        self.num_std = num_std

    def generate_signal(self, data: pd.DataFrame, symbol: str) -> dict:
        frame = data.copy().sort_values("datetime").reset_index(drop=True)
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce").ffill()
        frame = frame.dropna(subset=["close"]).reset_index(drop=True)
        if len(frame) < self.window:
            return _signal(symbol, "HOLD", 0.0, frame)

        recent = frame["close"].tail(self.window)
        mean = recent.mean()
        std = recent.std(ddof=0)
        current = recent.iloc[-1]
        if pd.isna(std) or std == 0:
            return _signal(symbol, "HOLD", 0.0, frame)

        lower = mean - self.num_std * std
        upper = mean + self.num_std * std
        distance = abs(current - mean) / (self.num_std * std)
        strength = min(float(distance), 1.0)
        if current < lower:
            return _signal(symbol, "BUY", strength, frame)
        if current > upper:
            return _signal(symbol, "SELL", strength, frame)
        return _signal(symbol, "HOLD", 0.0, frame)


def _signal(symbol: str, action: str, strength: float, frame: pd.DataFrame) -> dict:
    timestamp = pd.to_datetime(frame["datetime"]).iloc[-1] if not frame.empty else pd.Timestamp.utcnow()
    return {"symbol": symbol, "action": action, "strength": float(max(0.0, min(strength, 1.0))), "timestamp": timestamp}

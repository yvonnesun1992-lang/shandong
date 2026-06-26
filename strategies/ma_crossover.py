from __future__ import annotations

import pandas as pd


class MACrossoverStrategy:
    def __init__(self, short_window: int = 20, long_window: int = 60) -> None:
        if short_window <= 0 or long_window <= 0 or short_window >= long_window:
            raise ValueError("short_window must be positive and smaller than long_window")
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, data: pd.DataFrame, symbol: str) -> dict:
        frame = _prepare(data)
        if len(frame) < self.long_window:
            return _signal(symbol, "HOLD", 0.0, frame)

        short_ma = frame["close"].rolling(self.short_window).mean().iloc[-1]
        long_ma = frame["close"].rolling(self.long_window).mean().iloc[-1]
        if pd.isna(short_ma) or pd.isna(long_ma) or long_ma == 0:
            return _signal(symbol, "HOLD", 0.0, frame)

        spread = float((short_ma - long_ma) / abs(long_ma))
        strength = min(abs(spread) * 10, 1.0)
        if short_ma > long_ma:
            return _signal(symbol, "BUY", strength, frame)
        if short_ma < long_ma:
            return _signal(symbol, "SELL", strength, frame)
        return _signal(symbol, "HOLD", 0.0, frame)


def _prepare(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce").ffill()
    return frame.sort_values("datetime").dropna(subset=["close"]).reset_index(drop=True)


def _signal(symbol: str, action: str, strength: float, frame: pd.DataFrame) -> dict:
    timestamp = frame["datetime"].iloc[-1] if not frame.empty else pd.Timestamp.utcnow()
    return {"symbol": symbol, "action": action, "strength": float(max(0.0, min(strength, 1.0))), "timestamp": timestamp}

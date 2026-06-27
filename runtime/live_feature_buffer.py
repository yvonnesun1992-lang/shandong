from __future__ import annotations

from collections import defaultdict, deque
from math import isfinite
from typing import Any

import pandas as pd

from runtime.live_data_normalizer import normalize_live_tick


class LiveFeatureBuffer:
    def __init__(self, min_window: int = 60, max_window: int = 300) -> None:
        self.min_window = int(min_window)
        self.max_window = max(int(max_window), self.min_window)
        self._frames: dict[str, deque[dict]] = defaultdict(lambda: deque(maxlen=self.max_window))

    def append_tick(self, tick: dict[str, Any]) -> bool:
        normalized, reason = normalize_live_tick(tick)
        if reason:
            return False
        if float(normalized["close"]) <= 0 or not isfinite(float(normalized["close"])):
            return False
        symbol = str(normalized["symbol"]).upper()
        self._frames[symbol].append(normalized)
        self._frames[symbol] = deque(sorted(self._frames[symbol], key=lambda item: item["datetime"]), maxlen=self.max_window)
        return True

    def get_symbol_frame(self, symbol: str) -> pd.DataFrame:
        rows = list(self._frames.get(str(symbol).upper(), []))
        return _clean_frame(pd.DataFrame(rows))

    def get_all_frames(self) -> dict[str, pd.DataFrame]:
        return {symbol: self.get_symbol_frame(symbol) for symbol in sorted(self._frames)}

    def is_ready(self, symbol: str) -> bool:
        return len(self._frames.get(str(symbol).upper(), [])) >= self.min_window

    def clear(self) -> None:
        self._frames.clear()

    def status(self) -> dict:
        return {
            "min_window": self.min_window,
            "max_window": self.max_window,
            "symbols": sorted(self._frames),
            "ready": {symbol: self.is_ready(symbol) for symbol in sorted(self._frames)},
            "counts": {symbol: len(rows) for symbol, rows in sorted(self._frames.items())},
            "paper_trading": True,
            "real_trading": False,
            "broker_connected": False,
        }


def _clean_frame(frame: pd.DataFrame) -> pd.DataFrame:
    columns = ["datetime", "open", "high", "low", "close", "volume", "source"]
    if frame.empty:
        return pd.DataFrame(columns=columns)
    frame = frame.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.sort_values("datetime").dropna(subset=["open", "high", "low", "close"])
    frame = frame[frame["close"] > 0]
    return frame[columns].reset_index(drop=True)

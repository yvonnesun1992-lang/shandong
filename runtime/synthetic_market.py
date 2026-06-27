from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd


DEFAULT_SYMBOLS = ["AAPL", "MSFT", "NVDA", "JPM", "XOM", "JNJ", "PG", "UNH", "COST", "META"]


class SyntheticMarketGenerator:
    def __init__(self, seed: int = 42) -> None:
        self.seed = int(seed)

    def generate(self, mode: str = "trend", ticks: int = 1000, symbols: list[str] | None = None) -> pd.DataFrame:
        selected = symbols or DEFAULT_SYMBOLS
        rng = np.random.default_rng(self.seed)
        start = datetime(2026, 1, 1, 9, 30)
        rows = []
        for symbol_index, symbol in enumerate(selected):
            base = 100 + symbol_index * 7
            close = float(base)
            for tick in range(int(ticks)):
                drift, shock_scale = _mode_params(mode, tick, ticks)
                deterministic_wave = np.sin((tick + symbol_index) / 17) * 0.05
                shock = float(rng.normal(0, shock_scale))
                close = max(1.0, close * (1 + drift + deterministic_wave / 100 + shock))
                if mode == "crash" and tick > ticks * 0.35:
                    close = max(1.0, close * 0.995)
                open_price = close * (1 - 0.0005)
                high = max(open_price, close) * 1.002
                low = min(open_price, close) * 0.998
                rows.append(
                    {
                        "datetime": start + timedelta(minutes=tick),
                        "symbol": symbol,
                        "open": float(open_price),
                        "high": float(high),
                        "low": float(low),
                        "close": float(close),
                        "volume": int(10_000 + symbol_index * 100 + tick),
                    }
                )
        return pd.DataFrame(rows).sort_values(["datetime", "symbol"]).reset_index(drop=True)


def _mode_params(mode: str, tick: int, ticks: int) -> tuple[float, float]:
    normalized = tick / max(ticks, 1)
    if mode == "trend":
        return 0.00035, 0.001
    if mode == "sideways":
        return 0.0, 0.0015
    if mode == "volatile":
        return 0.00005, 0.006
    if mode == "crash":
        return (-0.004 if normalized > 0.35 else 0.0001), 0.004
    return 0.0001, 0.002


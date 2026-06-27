from __future__ import annotations

import pandas as pd


class MarketSimulator:
    def __init__(self, data: pd.DataFrame, mode: str = "replay") -> None:
        self.mode = mode
        self.data = data.copy()
        self.data["datetime"] = pd.to_datetime(self.data["datetime"])
        self.data = self.data.sort_values("datetime").reset_index(drop=True)
        self._index = 0
        self.is_open = False

    def open_market(self) -> None:
        self.is_open = True

    def close_market(self) -> None:
        self.is_open = False

    def market_is_open(self) -> bool:
        return self.is_open and self._index < len(self.data)

    def get_latest(self) -> dict | None:
        if not self.market_is_open():
            return None
        row = self.data.iloc[self._index].to_dict()
        self._index += 1
        return row

    def reset(self) -> None:
        self._index = 0
        self.is_open = False



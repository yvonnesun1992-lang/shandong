from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class MarketEvent:
    timestamp: pd.Timestamp
    bars: dict[str, dict]


class StreamingBuffer:
    def __init__(self, maxlen: int = 390) -> None:
        self.maxlen = int(maxlen)
        self._rows: dict[str, deque[dict]] = {}

    def append(self, event: MarketEvent) -> None:
        for symbol, bar in event.bars.items():
            self._rows.setdefault(symbol, deque(maxlen=self.maxlen)).append(dict(bar))

    def to_market_data(self) -> dict[str, pd.DataFrame]:
        return {
            symbol: pd.DataFrame(list(rows)).sort_values("datetime").reset_index(drop=True)
            for symbol, rows in self._rows.items()
            if rows
        }


class HistoricalReplayStream:
    def __init__(self, market_data: dict[str, pd.DataFrame], buffer_size: int = 390) -> None:
        self.market_data = _sanitize_market_data(market_data)
        self.buffer = StreamingBuffer(maxlen=buffer_size)
        self._timestamps = _common_timestamps(self.market_data)

    def __iter__(self):
        for timestamp in self._timestamps:
            bars = {}
            for symbol, frame in self.market_data.items():
                row = frame[frame["datetime"] == timestamp]
                if row.empty:
                    continue
                record = row.iloc[-1].to_dict()
                record["datetime"] = pd.Timestamp(record["datetime"])
                bars[symbol] = record
            if not bars:
                continue
            event = MarketEvent(timestamp=pd.Timestamp(timestamp), bars=bars)
            self.buffer.append(event)
            yield event

    def buffered_market_data(self) -> dict[str, pd.DataFrame]:
        return self.buffer.to_market_data()


class MockLiveDataAdapter(HistoricalReplayStream):
    """Mock live adapter for tests and local shadow deployment."""


def _sanitize_market_data(market_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    result = {}
    for symbol, frame in market_data.items():
        data = frame.copy()
        data["datetime"] = pd.to_datetime(data["datetime"])
        result[symbol] = data.sort_values("datetime").drop_duplicates("datetime").reset_index(drop=True)
    return result


def _common_timestamps(market_data: dict[str, pd.DataFrame]) -> pd.DatetimeIndex:
    common = None
    for frame in market_data.values():
        dates = pd.DatetimeIndex(frame["datetime"]).sort_values().unique()
        common = dates if common is None else common.intersection(dates)
    return pd.DatetimeIndex(common).sort_values() if common is not None else pd.DatetimeIndex([])

from __future__ import annotations

from datetime import UTC, datetime
from itertools import count
from math import sin
from typing import Protocol


class LiveMarketDataAdapter(Protocol):
    def get_latest_ticks(self) -> list[dict]:
        ...


class MockLiveMarketDataAdapter:
    def __init__(self, symbols: list[str] | None = None, base_price: float = 100.0) -> None:
        self.symbols = [str(symbol).upper() for symbol in (symbols or ["AAPL", "MSFT", "NVDA", "SPY", "QQQ"])]
        self.base_price = float(base_price)
        self._counter = count(1)

    def get_latest_ticks(self) -> list[dict]:
        step = next(self._counter)
        timestamp = datetime.now(UTC).replace(microsecond=0).isoformat()
        ticks = []
        for index, symbol in enumerate(self.symbols):
            price = self.base_price + index * 7.5 + sin(step / 3 + index) * 1.25 + step * 0.03
            ticks.append(_tick(timestamp, symbol, price, 1000 + step * 10 + index, "mock_live"))
        return ticks


class YFinancePollingAdapter:
    def __init__(self, symbols: list[str] | None = None, fallback: MockLiveMarketDataAdapter | None = None) -> None:
        self.symbols = [str(symbol).upper() for symbol in (symbols or ["AAPL", "MSFT", "NVDA", "SPY", "QQQ"])]
        self.fallback = fallback or MockLiveMarketDataAdapter(self.symbols)
        self.warning = ""

    def get_latest_ticks(self) -> list[dict]:
        try:
            import yfinance as yf  # type: ignore

            ticks = []
            timestamp = datetime.now(UTC).replace(microsecond=0).isoformat()
            for symbol in self.symbols:
                data = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=False)
                if data is None or data.empty:
                    raise RuntimeError("empty market data")
                row = data.tail(1).iloc[0]
                close = float(row.get("Close", row.get("close", 0.0)))
                open_price = float(row.get("Open", close))
                high = float(row.get("High", close))
                low = float(row.get("Low", close))
                volume = float(row.get("Volume", 0.0))
                ticks.append(
                    {
                        "datetime": timestamp,
                        "symbol": symbol,
                        "open": open_price,
                        "high": high,
                        "low": low,
                        "close": close,
                        "volume": volume,
                        "source": "yfinance",
                    }
                )
            self.warning = ""
            return ticks
        except Exception:
            self.warning = "yfinance unavailable; using mock live fallback"
            ticks = self.fallback.get_latest_ticks()
            for tick in ticks:
                tick["source"] = "mock_live"
            return ticks


def build_live_market_data_adapter(mode: str, symbols: list[str]) -> LiveMarketDataAdapter:
    if mode == "yfinance_polling":
        return YFinancePollingAdapter(symbols=symbols)
    return MockLiveMarketDataAdapter(symbols=symbols)


def _tick(timestamp: str, symbol: str, price: float, volume: float, source: str) -> dict:
    close = max(float(price), 0.01)
    return {
        "datetime": timestamp,
        "symbol": symbol,
        "open": round(close * 0.999, 6),
        "high": round(close * 1.002, 6),
        "low": round(close * 0.998, 6),
        "close": round(close, 6),
        "volume": float(volume),
        "source": source,
    }

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf


STANDARD_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]


class DataLoader:
    """Load and normalize historical market data for research and paper trading."""

    def __init__(self, cache_dir: str | Path = "data/cache/market") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_history(
        self,
        symbol: str,
        start: str | None = None,
        end: str | None = None,
        interval: str = "1d",
        use_cache: bool = True,
    ) -> pd.DataFrame:
        clean_symbol = self._safe_symbol(symbol)
        cache_path = self._cache_path(clean_symbol, start, end, interval)
        if use_cache and cache_path.exists():
            return self._standardize(pd.read_csv(cache_path), datetime_column="datetime")

        raw = yf.download(clean_symbol, start=start, end=end, interval=interval, auto_adjust=False, progress=False)
        data = self._standardize(raw)
        data.to_csv(cache_path, index=False)
        return data

    def _cache_path(self, symbol: str, start: str | None, end: str | None, interval: str) -> Path:
        safe_start = start or "none"
        safe_end = end or "none"
        return self.cache_dir / f"{symbol}_{safe_start}_{safe_end}_{interval}.csv"

    @staticmethod
    def _safe_symbol(symbol: str) -> str:
        clean = "".join(ch for ch in symbol.upper().strip() if ch.isalnum() or ch in {".", "-", "_"})
        if not clean:
            raise ValueError("symbol cannot be empty")
        return clean

    @staticmethod
    def _standardize(data: pd.DataFrame, datetime_column: str | None = None) -> pd.DataFrame:
        if data is None or data.empty:
            return pd.DataFrame(columns=STANDARD_COLUMNS)

        frame = data.copy()
        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = [str(col[0]).lower() for col in frame.columns]
        else:
            frame.columns = [str(col).strip().lower() for col in frame.columns]

        if datetime_column and datetime_column in frame.columns:
            frame["datetime"] = pd.to_datetime(frame[datetime_column])
        elif "date" in frame.columns:
            frame["datetime"] = pd.to_datetime(frame["date"])
        else:
            frame = frame.reset_index()
            index_col = "date" if "date" in frame.columns else frame.columns[0]
            frame["datetime"] = pd.to_datetime(frame[index_col])

        rename_map = {
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "adj close": "close",
            "volume": "volume",
        }
        normalized = pd.DataFrame({"datetime": frame["datetime"]})
        for source, target in rename_map.items():
            if source in frame.columns and target not in normalized:
                normalized[target] = pd.to_numeric(frame[source], errors="coerce")

        for column in STANDARD_COLUMNS:
            if column not in normalized:
                normalized[column] = 0 if column == "volume" else pd.NA

        normalized = normalized[STANDARD_COLUMNS].sort_values("datetime").reset_index(drop=True)
        numeric_columns = ["open", "high", "low", "close", "volume"]
        normalized[numeric_columns] = normalized[numeric_columns].ffill().bfill().fillna(0)
        return normalized

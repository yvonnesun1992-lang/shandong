from __future__ import annotations

from pathlib import Path

import pandas as pd


STANDARD_COLUMNS = ["date", "open", "high", "low", "close", "volume"]
SAMPLE_FILES = {
    ("us", "NVDA"): "us_NVDA.csv",
    ("cn", "300308"): "cn_300308.csv",
}


def sample_data_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "sample"


def load_sample_ohlcv(market: str, symbol: str) -> pd.DataFrame:
    """Load local sample OHLCV data for demos and tests."""
    key = (market.lower(), symbol.upper())
    file_name = SAMPLE_FILES.get(key)
    if file_name is None:
        available = ", ".join(f"{item[0]}:{item[1]}" for item in SAMPLE_FILES)
        raise ValueError(f"No sample data for {market}:{symbol}. Available samples: {available}")

    path = sample_data_dir() / file_name
    if not path.exists():
        raise FileNotFoundError(f"Sample data file not found: {path}")

    data = pd.read_csv(path)
    missing = [column for column in STANDARD_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Sample data missing columns: {missing}")

    result = data[STANDARD_COLUMNS].copy()
    result["date"] = pd.to_datetime(result["date"])
    numeric_columns = ["open", "high", "low", "close", "volume"]
    result[numeric_columns] = result[numeric_columns].apply(pd.to_numeric, errors="coerce")
    result = result.dropna().sort_values("date").reset_index(drop=True)
    result.attrs["is_sample_data"] = True
    result.attrs["data_source"] = "sample"
    result.attrs["sample_market"] = market.lower()
    result.attrs["sample_symbol"] = symbol.upper()
    return result

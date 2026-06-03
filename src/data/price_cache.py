from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PRICE_CACHE_DIR = PROJECT_ROOT / "data" / "cache"
STANDARD_COLUMNS = ["date", "open", "high", "low", "close", "volume"]
ALLOWED_MARKETS = {"us", "cn"}


def _normalize_market(market: str) -> str:
    clean_market = str(market).strip().lower()
    if clean_market not in ALLOWED_MARKETS:
        raise ValueError("market must be 'us' or 'cn'.")
    return clean_market


def _normalize_symbol(symbol: str) -> str:
    clean_symbol = str(symbol).strip().upper()
    if not clean_symbol:
        raise ValueError("symbol cannot be empty.")
    if clean_symbol in {".", ".."} or "/" in clean_symbol or "\\" in clean_symbol:
        raise ValueError("symbol cannot contain path characters.")
    if ".." in clean_symbol:
        raise ValueError("symbol cannot contain path traversal.")
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    if any(character not in allowed for character in clean_symbol):
        raise ValueError("symbol contains unsupported characters.")
    if clean_symbol.isdigit() and len(clean_symbol) <= 6:
        clean_symbol = clean_symbol.zfill(6)
    return clean_symbol


def _cache_dir(cache_dir: str | Path) -> Path:
    path = Path(cache_dir).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_path(market: str, symbol: str, cache_dir: str | Path) -> Path:
    clean_market = _normalize_market(market)
    clean_symbol = _normalize_symbol(symbol)
    base_dir = _cache_dir(cache_dir)
    path = (base_dir / f"{clean_market}_{clean_symbol}.csv").resolve()
    if base_dir != path.parent:
        raise ValueError("cache path must stay inside the cache directory.")
    return path


def _standardize_ohlcv(data: pd.DataFrame, source: str) -> pd.DataFrame:
    missing = [column for column in STANDARD_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"{source} missing OHLCV columns: {missing}")

    result = data[STANDARD_COLUMNS].copy()
    try:
        result["date"] = pd.to_datetime(result["date"])
        numeric_columns = ["open", "high", "low", "close", "volume"]
        result[numeric_columns] = result[numeric_columns].apply(pd.to_numeric, errors="raise")
    except Exception as error:
        raise ValueError(f"{source} contains invalid OHLCV values.") from error

    result = result.sort_values("date").reset_index(drop=True)
    if result.empty:
        raise ValueError(f"{source} is empty.")
    return result


def cache_price_data(
    market: str,
    symbol: str,
    data: pd.DataFrame,
    cache_dir: str | Path = DEFAULT_PRICE_CACHE_DIR,
) -> Path:
    """Save standard OHLCV data to a local CSV cache file."""
    path = _cache_path(market, symbol, cache_dir)
    result = _standardize_ohlcv(data, f"price cache data for {market}:{symbol}")
    result.to_csv(path, index=False)
    return path


def load_cached_price_data(
    market: str,
    symbol: str,
    cache_dir: str | Path = DEFAULT_PRICE_CACHE_DIR,
) -> pd.DataFrame:
    """Load standard OHLCV data from the local CSV cache."""
    path = _cache_path(market, symbol, cache_dir)
    if not path.exists():
        raise FileNotFoundError(f"Cached price data not found: {path.name}")

    try:
        data = pd.read_csv(path)
        result = _standardize_ohlcv(data, f"cached price data {path.name}")
    except FileNotFoundError:
        raise
    except Exception as error:
        raise ValueError(f"Cached price data is invalid: {path.name}") from error

    result.attrs["data_source"] = "cache"
    result.attrs["is_sample_data"] = False
    result.attrs["market"] = _normalize_market(market)
    result.attrs["symbol"] = _normalize_symbol(symbol)
    return result


def has_cached_price_data(
    market: str,
    symbol: str,
    cache_dir: str | Path = DEFAULT_PRICE_CACHE_DIR,
) -> bool:
    return _cache_path(market, symbol, cache_dir).exists()


def get_cache_metadata(
    market: str,
    symbol: str,
    cache_dir: str | Path = DEFAULT_PRICE_CACHE_DIR,
) -> dict:
    path = _cache_path(market, symbol, cache_dir)
    if not path.exists():
        raise FileNotFoundError(f"Cached price data not found: {path.name}")
    data = load_cached_price_data(market, symbol, cache_dir)
    return {
        "market": _normalize_market(market),
        "symbol": _normalize_symbol(symbol),
        "rows": int(len(data)),
        "start_date": data["date"].min().date().isoformat(),
        "end_date": data["date"].max().date().isoformat(),
        "file_size": int(path.stat().st_size),
        "path": str(path),
    }


def delete_cached_price_data(
    market: str,
    symbol: str,
    cache_dir: str | Path = DEFAULT_PRICE_CACHE_DIR,
) -> None:
    path = _cache_path(market, symbol, cache_dir)
    if path.exists():
        path.unlink()


def list_cached_symbols(cache_dir: str | Path = DEFAULT_PRICE_CACHE_DIR) -> pd.DataFrame:
    base_dir = _cache_dir(cache_dir)
    rows = []
    for path in sorted(base_dir.glob("*.csv")):
        stem_parts = path.stem.split("_", 1)
        if len(stem_parts) != 2:
            continue
        market, symbol = stem_parts
        try:
            rows.append(get_cache_metadata(market, symbol, base_dir))
        except ValueError as error:
            raise ValueError(f"Cached price data is invalid: {path.name}") from error
    return pd.DataFrame(rows, columns=["market", "symbol", "rows", "start_date", "end_date", "file_size", "path"])

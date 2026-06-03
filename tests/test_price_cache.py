from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data.price_cache import (
    cache_price_data,
    delete_cached_price_data,
    get_cache_metadata,
    has_cached_price_data,
    list_cached_symbols,
    load_cached_price_data,
)
from src.data.sample_data import load_sample_ohlcv


def test_cache_price_data_save_and_load(tmp_path):
    data = load_sample_ohlcv("us", "NVDA")

    path = cache_price_data("us", "NVDA", data, tmp_path)
    loaded = load_cached_price_data("us", "NVDA", tmp_path)

    assert path.name == "us_NVDA.csv"
    assert path.exists()
    assert len(loaded) == len(data)
    assert pd.api.types.is_datetime64_any_dtype(loaded["date"])
    assert loaded.attrs["data_source"] == "cache"
    assert loaded.attrs["market"] == "us"
    assert loaded.attrs["symbol"] == "NVDA"


def test_cache_metadata_and_delete(tmp_path):
    data = load_sample_ohlcv("cn", "300308")
    cache_price_data("cn", "300308", data, tmp_path)

    metadata = get_cache_metadata("cn", "300308", tmp_path)
    assert metadata["market"] == "cn"
    assert metadata["symbol"] == "300308"
    assert metadata["rows"] >= 120
    assert metadata["file_size"] > 0
    assert has_cached_price_data("cn", "300308", tmp_path) is True

    delete_cached_price_data("cn", "300308", tmp_path)
    assert has_cached_price_data("cn", "300308", tmp_path) is False


def test_list_cached_symbols_empty_returns_empty_dataframe(tmp_path):
    table = list_cached_symbols(tmp_path)

    assert table.empty
    assert list(table.columns) == ["market", "symbol", "rows", "start_date", "end_date", "file_size", "path"]


def test_list_cached_symbols_returns_cache_rows(tmp_path):
    cache_price_data("us", "NVDA", load_sample_ohlcv("us", "NVDA"), tmp_path)
    cache_price_data("cn", "300308", load_sample_ohlcv("cn", "300308"), tmp_path)

    table = list_cached_symbols(tmp_path)

    assert set(table["market"]) == {"us", "cn"}
    assert set(table["symbol"]) == {"NVDA", "300308"}


def test_cache_rejects_invalid_market(tmp_path):
    with pytest.raises(ValueError, match="market"):
        cache_price_data("hk", "000001", load_sample_ohlcv("us", "NVDA"), tmp_path)


def test_cache_rejects_path_traversal_symbol(tmp_path):
    with pytest.raises(ValueError, match="path"):
        cache_price_data("us", "../secret", load_sample_ohlcv("us", "NVDA"), tmp_path)

    assert list(Path(tmp_path).glob("*.csv")) == []


def test_load_damaged_cache_raises_value_error(tmp_path):
    (tmp_path / "us_NVDA.csv").write_text("not,a,valid,ohlcv\n1,2,3,4\n", encoding="utf-8")

    with pytest.raises(ValueError, match="us_NVDA.csv"):
        load_cached_price_data("us", "NVDA", tmp_path)


def test_cache_file_does_not_save_sensitive_keys(tmp_path):
    path = cache_price_data("us", "NVDA", load_sample_ohlcv("us", "NVDA"), tmp_path)
    text = path.read_text(encoding="utf-8").lower()

    for word in ["api_key", "secret", "password", "token"]:
        assert word not in text

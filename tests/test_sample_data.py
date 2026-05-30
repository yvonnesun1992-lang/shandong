import pandas as pd

from src.backtest.simple_backtest import run_simple_backtest
from src.data.cn_data import get_cn_ohlcv
from src.data.sample_data import STANDARD_COLUMNS, load_sample_ohlcv
from src.data.us_data import get_us_ohlcv
from src.indicators.technical import add_technical_indicators


def test_load_us_sample_ohlcv():
    data = load_sample_ohlcv("us", "NVDA")

    assert list(data.columns) == STANDARD_COLUMNS
    assert len(data) >= 120
    assert pd.api.types.is_datetime64_any_dtype(data["date"])
    assert data["volume"].gt(0).all()
    assert data.attrs["is_sample_data"] is True
    assert data["high"].ge(data[["open", "close", "low"]].max(axis=1)).all()
    assert data["low"].le(data[["open", "close", "high"]].min(axis=1)).all()


def test_load_cn_sample_ohlcv():
    data = load_sample_ohlcv("cn", "300308")

    assert list(data.columns) == STANDARD_COLUMNS
    assert len(data) >= 120
    assert pd.api.types.is_datetime64_any_dtype(data["date"])
    assert data["volume"].gt(0).all()
    assert data.attrs["is_sample_data"] is True
    assert data["high"].ge(data[["open", "close", "low"]].max(axis=1)).all()
    assert data["low"].le(data[["open", "close", "high"]].min(axis=1)).all()


def test_indicators_work_with_sample_data():
    data = load_sample_ohlcv("us", "NVDA")

    result = add_technical_indicators(data)

    assert {"ma20", "ma60", "ma120", "rsi14", "volume_ma20"}.issubset(result.columns)
    assert not result["ma120"].dropna().empty


def test_backtest_runs_with_sample_data():
    data = load_sample_ohlcv("cn", "300308")

    result = run_simple_backtest(data)

    assert result["final_portfolio_value"] > 0
    assert result["number_of_trades"] >= 0


def test_us_data_fallback_sets_sample_attrs(monkeypatch):
    def fail_download(*args, **kwargs):
        raise RuntimeError("network unavailable")

    monkeypatch.setattr("src.data.us_data.yf.download", fail_download)

    data = get_us_ohlcv("AMD")

    assert data.attrs["data_source"] == "sample"
    assert data.attrs["is_sample_data"] is True
    assert "network unavailable" in data.attrs["fallback_reason"]


def test_cn_data_fallback_sets_sample_attrs(monkeypatch):
    def fail_hist(*args, **kwargs):
        raise RuntimeError("network unavailable")

    monkeypatch.setattr("src.data.cn_data.ak.stock_zh_a_hist", fail_hist)

    data = get_cn_ohlcv("000001")

    assert data.attrs["data_source"] == "sample"
    assert data.attrs["is_sample_data"] is True
    assert "network unavailable" in data.attrs["fallback_reason"]

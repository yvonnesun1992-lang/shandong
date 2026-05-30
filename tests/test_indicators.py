import pandas as pd

from src.indicators.technical import add_technical_indicators, moving_average, rsi


def test_moving_average_uses_window_mean():
    series = pd.Series([1, 2, 3, 4, 5])

    result = moving_average(series, 3)

    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])
    assert result.iloc[2] == 2
    assert result.iloc[4] == 4


def test_rsi_is_100_when_price_only_rises():
    series = pd.Series(range(1, 21))

    result = rsi(series, 14)

    assert result.iloc[-1] == 100


def test_add_technical_indicators_adds_expected_columns():
    data = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=130),
            "open": range(130),
            "high": range(130),
            "low": range(130),
            "close": range(130),
            "volume": range(1000, 1130),
        }
    )

    result = add_technical_indicators(data)

    assert {"ma20", "ma60", "ma120", "rsi14", "volume_ma20"}.issubset(result.columns)
    assert not pd.isna(result.iloc[-1]["ma120"])

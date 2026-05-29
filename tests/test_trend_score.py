import pandas as pd

from src.strategies.trend_score import add_trend_scores, calculate_trend_score, score_status


def test_calculate_trend_score_can_reach_100():
    row = pd.Series(
        {
            "close": 130,
            "ma20": 120,
            "ma60": 100,
            "ma120": 80,
            "rsi14": 60,
            "volume": 2000,
            "volume_ma20": 1000,
        }
    )

    assert calculate_trend_score(row) == 100


def test_score_status_ranges():
    assert score_status(85) == "Strong trend"
    assert score_status(65) == "Watchlist"
    assert score_status(45) == "Neutral"
    assert score_status(20) == "Weak"


def test_add_trend_scores_adds_score_and_status():
    data = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=140),
            "open": range(1, 141),
            "high": range(2, 142),
            "low": range(0, 140),
            "close": range(1, 141),
            "volume": range(1000, 1140),
        }
    )

    result = add_trend_scores(data)

    assert "trend_score" in result.columns
    assert "trend_status" in result.columns
    assert result.iloc[-1]["trend_score"] >= 80

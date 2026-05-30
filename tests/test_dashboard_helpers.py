from __future__ import annotations

import pandas as pd

from app.main import data_source_label, trend_scores_to_csv
from src.data.sample_data import load_sample_ohlcv
from src.strategies.trend_score import latest_trend_score


def test_trend_scores_to_csv_uses_export_column_names():
    rank_table = pd.DataFrame(
        [
            {
                "股票代码": "NVDA",
                "趋势分数": 90,
                "状态": "Strong trend",
                "收盘价": 79.41,
                "RSI14": 62.5,
                "数据来源": "示例数据",
            }
        ]
    )

    csv_text = trend_scores_to_csv(rank_table).decode("utf-8-sig")

    assert "symbol,score,status,close,rsi14,data_source" in csv_text
    assert "NVDA,90,Strong trend,79.41,62.5,示例数据" in csv_text


def test_data_source_label_reads_sample_attrs():
    data = load_sample_ohlcv("us", "NVDA")

    assert data_source_label(data) == "示例数据"


def test_sample_data_can_generate_latest_trend_score():
    data = load_sample_ohlcv("cn", "300308")

    score = latest_trend_score("300308", data)

    assert score.symbol == "300308"
    assert 0 <= score.score <= 100
    assert score.status in {"Strong trend", "Watchlist", "Neutral", "Weak"}

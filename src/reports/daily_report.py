from __future__ import annotations

import pandas as pd

from src.strategies.trend_score import latest_trend_score


def build_score_report(symbol_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build a ranking table from many symbols and their OHLCV data."""
    rows = []
    for symbol, data in symbol_data.items():
        score = latest_trend_score(symbol, data)
        rows.append(
            {
                "symbol": score.symbol,
                "score": score.score,
                "status": score.status,
                "close": score.close,
                "rsi14": score.rsi14,
            }
        )
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)

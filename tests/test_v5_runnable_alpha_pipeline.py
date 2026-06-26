from __future__ import annotations

import numpy as np
import pandas as pd


def test_v5_build_factor_matrices_from_market_data():
    from quant_core_v5.pipeline import build_factor_matrices_from_market_data

    market_data = {
        "AAPL": _market_frame(0.8),
        "TSLA": _market_frame(0.3),
        "NVDA": _market_frame(0.5),
    }
    result = build_factor_matrices_from_market_data(market_data, factors=["momentum_20d", "trend_strength"])

    assert set(result["factor_matrices"]) == {"momentum_20d", "trend_strength"}
    assert list(result["price_matrix"].columns) == ["AAPL", "TSLA", "NVDA"]
    assert not result["factor_matrices"]["momentum_20d"].dropna(how="all").empty
    assert result["price_matrix"].index.is_monotonic_increasing


def test_v5_run_alpha_pipeline_from_market_data_returns_auditable_result():
    from quant_core_v5.pipeline import run_alpha_pipeline_from_market_data

    market_data = {
        "AAPL": _market_frame(0.8),
        "TSLA": _market_frame(0.3),
        "NVDA": _market_frame(0.5),
    }
    result = run_alpha_pipeline_from_market_data(
        market_data=market_data,
        factors=["momentum_20d", "trend_strength"],
        regime={"state": "bull", "confidence": 0.7},
        max_weight_per_asset=0.40,
    )

    assert result["version"] == "V5.0-alpha-system"
    assert {"factor", "alpha", "portfolio", "summary", "safety"} <= set(result)
    assert result["portfolio"]["backtest"]["portfolio_returns"].index.min() > result["portfolio"]["weights"].index.min()
    assert result["summary"]["no_broker_connection"] is True
    assert result["summary"]["causal_backtest"] is True
    assert result["safety"]["real_trading"] is False


def _market_frame(drift: float, days: int = 90) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=days, freq="D")
    close = 100 + np.arange(days) * drift + np.sin(np.arange(days) / 5)
    return pd.DataFrame(
        {
            "datetime": dates,
            "open": close - 0.2,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": 1000 + np.arange(days),
        }
    )

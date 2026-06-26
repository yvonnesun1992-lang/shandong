from __future__ import annotations

import numpy as np
import pandas as pd


def sample_asset(symbol: str, days: int = 120, drift: float = 0.3, phase: float = 0.0) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=days, freq="D")
    index = np.arange(days)
    close = 100 + index * drift + np.sin(index / 5 + phase) * 1.5
    return pd.DataFrame(
        {
            "datetime": dates,
            "symbol": symbol,
            "open": close - 0.4,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": 1000 + index,
        }
    )


def sample_universe() -> dict[str, pd.DataFrame]:
    return {
        "AAPL": sample_asset("AAPL", drift=0.45, phase=0.0),
        "TSLA": sample_asset("TSLA", drift=0.20, phase=0.8),
        "NVDA": sample_asset("NVDA", drift=-0.05, phase=1.4),
    }


def test_factor_generation_includes_v12_columns_without_nan():
    from feature_engine.factors import calculate_factors

    factors = calculate_factors(sample_asset("AAPL", drift=0.4))
    expected = {
        "momentum_5d",
        "momentum_10d",
        "momentum_20d",
        "momentum_60d",
        "zscore_price",
        "price_distance_ma20",
        "bollinger_position",
        "realized_vol_5d",
        "realized_vol_20d",
        "volatility_change",
        "ma_slope_20",
        "trend_strength",
        "breakout_strength",
    }

    assert expected <= set(factors.columns)
    assert not factors[list(expected)].tail(20).isna().any().any()
    assert factors["momentum_20d"].iloc[-1] > 0


def test_factor_builder_outputs_date_by_asset_matrix():
    from factor_engine.factor_builder import FactorBuilder

    matrix = FactorBuilder().build_factor_matrix(sample_universe(), "momentum_20d")

    assert isinstance(matrix.index, pd.DatetimeIndex)
    assert list(matrix.columns) == ["AAPL", "TSLA", "NVDA"]
    assert matrix.index.is_monotonic_increasing
    assert not matrix.tail(20).isna().any().any()


def test_ic_calculation_uses_future_returns_without_lookahead():
    from evaluation.ic_analysis import calculate_factor_ic
    from factor_engine.factor_builder import FactorBuilder

    universe = sample_universe()
    builder = FactorBuilder()
    factor_matrix = builder.build_factor_matrix(universe, "momentum_20d")
    price_matrix = builder.build_price_matrix(universe)
    result = calculate_factor_ic("momentum_20d", factor_matrix, price_matrix, forward_days=5)

    assert result["factor"] == "momentum_20d"
    assert {"ic_mean", "ic_std", "ic_ir", "ic_stability", "rolling_ic_5", "rolling_ic_10", "rolling_ic_20"} <= set(result)
    assert isinstance(result["ic_series"], pd.Series)
    assert result["ic_series"].index.max() < price_matrix.index.max()
    assert np.isfinite(result["ic_mean"])


def test_factor_scoring_ranks_top_factors():
    from evaluation.factor_scoring import score_factors

    table = score_factors(
        [
            {"factor": "momentum_20d", "ic_mean": 0.05, "ic_ir": 2.0, "ic_stability": 0.8, "turnover_penalty": 0.01},
            {"factor": "zscore_price", "ic_mean": -0.02, "ic_ir": -0.5, "ic_stability": 0.4, "turnover_penalty": 0.02},
            {"factor": "trend_strength", "ic_mean": 0.03, "ic_ir": 1.5, "ic_stability": 0.7, "turnover_penalty": 0.005},
        ]
    )

    assert list(table["factor"])[:2] == ["momentum_20d", "trend_strength"]
    assert "score" in table.columns
    assert table.iloc[0]["score"] > table.iloc[-1]["score"]


def test_factor_selection_returns_best_and_rejected_with_reasons():
    from selection.factor_selector import FactorSelector

    selected = FactorSelector(stability_threshold=0.6).select(
        [
            {"factor": "momentum_20d", "ic_mean": 0.05, "ic_ir": 2.0, "ic_stability": 0.8},
            {"factor": "weak_factor", "ic_mean": 0.01, "ic_ir": 0.5, "ic_stability": 0.8},
            {"factor": "unstable_factor", "ic_mean": 0.04, "ic_ir": 1.5, "ic_stability": 0.2},
            {"factor": "negative_factor", "ic_mean": -0.03, "ic_ir": 1.2, "ic_stability": 0.9},
        ]
    )

    assert selected["best_factors"] == ["momentum_20d"]
    rejected = {item["factor"]: item["reason"] for item in selected["rejected_factors"]}
    assert "ic_ir<=1" in rejected["weak_factor"]
    assert "stability_below_threshold" in rejected["unstable_factor"]
    assert "ic<=0" in rejected["negative_factor"]


def test_factor_portfolio_normalizes_weights_and_simulates_returns():
    from factor_engine.factor_builder import FactorBuilder
    from portfolio.factor_portfolio import FactorPortfolioSimulator

    universe = sample_universe()
    builder = FactorBuilder()
    matrices = {
        "momentum_20d": builder.build_factor_matrix(universe, "momentum_20d"),
        "trend_strength": builder.build_factor_matrix(universe, "trend_strength"),
    }
    price_matrix = builder.build_price_matrix(universe)
    simulation = FactorPortfolioSimulator().simulate(
        factor_matrices=matrices,
        price_matrix=price_matrix,
        factor_scores={"momentum_20d": 0.08, "trend_strength": 0.04},
        forward_days=1,
    )

    assert abs(sum(simulation["factor_weights"].values()) - 1.0) < 1e-9
    assert set(simulation["factor_weights"]) == {"momentum_20d", "trend_strength"}
    assert not simulation["portfolio_returns"].dropna().empty
    assert "cumulative_return" in simulation
    assert np.isfinite(simulation["cumulative_return"])


def test_factor_report_generates_markdown_and_charts():
    from reporting.factor_report import generate_factor_report

    score_table = pd.DataFrame(
        [
            {"factor": "momentum_20d", "ic_mean": 0.05, "ic_ir": 2.0, "ic_stability": 0.8, "score": 0.07},
            {"factor": "trend_strength", "ic_mean": 0.03, "ic_ir": 1.5, "ic_stability": 0.7, "score": 0.03},
        ]
    )
    report = generate_factor_report(
        score_table=score_table,
        ic_results={"momentum_20d": {"ic_series": pd.Series([0.1, 0.0, 0.05], index=pd.date_range("2024-01-01", periods=3))}},
        portfolio_result={"portfolio_returns": pd.Series([0.01, -0.002, 0.004], index=pd.date_range("2024-01-01", periods=3))},
    )

    assert "Quant Factor Research Report" in report["markdown"]
    assert {"ic_curve", "factor_ranking", "cumulative_factor_returns"} <= set(report["figures"])

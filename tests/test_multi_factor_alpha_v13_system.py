from __future__ import annotations

import numpy as np
import pandas as pd


def sample_alpha_inputs() -> tuple[dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame]:
    dates = pd.date_range("2024-01-01", periods=24, freq="D")
    factor_matrices = {
        "momentum_20d": pd.DataFrame(
            {
                "AAPL": np.linspace(-1.0, 1.0, len(dates)),
                "TSLA": np.linspace(0.4, -0.4, len(dates)),
                "NVDA": np.sin(np.arange(len(dates)) / 3),
            },
            index=dates,
        ),
        "mean_reversion": pd.DataFrame(
            {
                "AAPL": np.linspace(0.5, -0.5, len(dates)),
                "TSLA": np.linspace(-0.2, 0.8, len(dates)),
                "NVDA": np.cos(np.arange(len(dates)) / 4),
            },
            index=dates,
        ),
        "trend_strength": pd.DataFrame(
            {
                "AAPL": np.linspace(0.1, 0.8, len(dates)),
                "TSLA": np.linspace(0.3, 0.1, len(dates)),
                "NVDA": np.linspace(0.2, 0.6, len(dates)),
            },
            index=dates,
        ),
    }
    price_matrix = pd.DataFrame(
        {
            "AAPL": 100 + np.arange(len(dates)) * 0.8,
            "TSLA": 90 + np.sin(np.arange(len(dates)) / 2) * 3 + np.arange(len(dates)) * 0.2,
            "NVDA": 70 + np.arange(len(dates)) * 0.5,
        },
        index=dates,
    )
    returns = price_matrix.pct_change().fillna(0.0)
    return factor_matrices, price_matrix, returns


def test_normalization_zscore_and_winsorization_are_cross_sectional_and_time_safe():
    from alpha_engine.normalization import normalize_factor_matrix

    dates = pd.date_range("2024-01-01", periods=3, freq="D")
    matrix = pd.DataFrame(
        {
            "A": [1.0, np.nan, 100.0],
            "B": [2.0, 2.0, 3.0],
            "C": [3.0, 3.0, 4.0],
        },
        index=dates,
    )
    normalized = normalize_factor_matrix(matrix, winsor_limits=(0.01, 0.99))

    assert pd.isna(normalized.loc[dates[0], "A"]) is False
    assert pd.isna(normalized.loc[dates[1], "A"])
    assert normalized.loc[dates[2], "A"] < 5
    row = normalized.loc[dates[0]].dropna()
    assert abs(float(row.mean())) < 1e-9


def test_factor_weighting_uses_softmax_ic_ir_and_recent_decay():
    from weighting.factor_weighting import compute_factor_weights

    weights = compute_factor_weights(
        [
            {"factor": "momentum_20d", "ic_mean": 0.05, "ic_ir": 2.0, "ic_stability": 0.8, "rolling_ic_20": pd.Series([0.01, 0.04, 0.07])},
            {"factor": "mean_reversion", "ic_mean": 0.02, "ic_ir": 1.1, "ic_stability": 0.7, "rolling_ic_20": pd.Series([0.03, 0.02, 0.01])},
            {"factor": "trend_strength", "ic_mean": 0.03, "ic_ir": 1.5, "ic_stability": 0.9, "rolling_ic_20": pd.Series([0.02, 0.03, 0.05])},
        ]
    )

    assert abs(sum(weights.values()) - 1.0) < 1e-9
    assert weights["momentum_20d"] > weights["mean_reversion"]
    assert all(value > 0 for value in weights.values())


def test_regime_adjuster_overweights_matching_factor_family():
    from regime.regime_adjuster import RegimeAdjuster

    base = {"momentum_20d": 0.4, "mean_reversion": 0.3, "trend_strength": 0.3}
    bull = RegimeAdjuster().adjust(base, {"state": "bull", "confidence": 0.8})
    bear = RegimeAdjuster().adjust(base, {"state": "bear", "confidence": 0.8})
    sideways = RegimeAdjuster().adjust(base, {"state": "sideways", "confidence": 0.8})

    assert bull["momentum_20d"] > base["momentum_20d"]
    assert bear["mean_reversion"] > base["mean_reversion"]
    assert abs(sideways["momentum_20d"] - sideways["mean_reversion"]) < 0.05
    assert abs(sum(bull.values()) - 1.0) < 1e-9


def test_alpha_model_builds_weighted_alpha_scores_without_future_fill():
    from alpha_engine.alpha_model import AlphaModel

    factor_matrices, _, _ = sample_alpha_inputs()
    alpha = AlphaModel().build_alpha_scores(
        factor_matrices=factor_matrices,
        factor_weights={"momentum_20d": 0.5, "mean_reversion": 0.2, "trend_strength": 0.3},
    )

    assert isinstance(alpha, pd.DataFrame)
    assert list(alpha.columns) == ["AAPL", "TSLA", "NVDA"]
    assert not alpha.dropna(how="all").empty
    assert alpha.index.is_monotonic_increasing


def test_multi_factor_portfolio_respects_single_asset_cap_and_leverage():
    from portfolio.multi_factor_portfolio import MultiFactorPortfolio

    dates = pd.date_range("2024-01-01", periods=2, freq="D")
    alpha_scores = pd.DataFrame(
        {
            "AAPL": [2.0, 1.0],
            "TSLA": [1.8, -0.5],
            "NVDA": [0.5, 0.2],
            "MSFT": [0.1, 0.1],
            "AMZN": [-0.2, 0.0],
            "META": [0.7, 0.3],
            "GOOG": [0.9, 0.4],
            "NFLX": [0.3, 0.1],
            "AMD": [0.4, 0.2],
            "ORCL": [0.2, 0.2],
        },
        index=dates,
    )

    weights = MultiFactorPortfolio(max_weight_per_asset=0.10).construct(alpha_scores)

    assert (weights.sum(axis=1).round(8) == 1.0).all()
    assert float(weights.max().max()) <= 0.10 + 1e-9
    assert float(weights.min().min()) >= 0.0


def test_risk_engine_reduces_exposure_on_drawdown_and_volatility():
    from risk.risk_engine import RiskEngine

    engine = RiskEngine(max_position_per_asset=0.10, max_drawdown=0.10, high_volatility_threshold=0.20)
    weights = pd.Series({"AAPL": 0.10, "TSLA": 0.10, "NVDA": 0.08})
    adjusted = engine.adjust_portfolio_weights(
        weights=weights,
        current_drawdown=0.15,
        portfolio_volatility=0.30,
    )

    assert adjusted["exposure_multiplier"] < 1.0
    assert adjusted["adjusted_weights"].sum() < weights.sum()
    assert float(adjusted["adjusted_weights"].max()) <= 0.10 + 1e-9


def test_attribution_outputs_factor_return_risk_and_correlation():
    from evaluation.attribution import analyze_factor_attribution

    factor_returns = pd.DataFrame(
        {
            "momentum_20d": [0.01, 0.02, -0.005, 0.01],
            "mean_reversion": [0.002, -0.001, 0.003, 0.002],
            "trend_strength": [0.005, 0.004, 0.006, 0.005],
        },
        index=pd.date_range("2024-01-01", periods=4, freq="D"),
    )
    factor_weights = {"momentum_20d": 0.5, "mean_reversion": 0.2, "trend_strength": 0.3}
    attribution = analyze_factor_attribution(factor_returns, factor_weights)

    assert {"return_contribution", "risk_contribution", "correlation_matrix"} <= set(attribution)
    assert attribution["correlation_matrix"].shape == (3, 3)
    assert "momentum_20d" in attribution["return_contribution"]


def test_multi_factor_backtest_is_causal_and_returns_metrics():
    from alpha_engine.alpha_model import AlphaModel
    from evaluation.multi_factor_backtest import MultiFactorBacktest
    from portfolio.multi_factor_portfolio import MultiFactorPortfolio

    factor_matrices, price_matrix, _ = sample_alpha_inputs()
    alpha_scores = AlphaModel().build_alpha_scores(
        factor_matrices=factor_matrices,
        factor_weights={"momentum_20d": 0.4, "mean_reversion": 0.2, "trend_strength": 0.4},
    )
    portfolio_weights = MultiFactorPortfolio(max_weight_per_asset=0.40).construct(alpha_scores)
    result = MultiFactorBacktest().run(portfolio_weights=portfolio_weights, price_matrix=price_matrix, regime={"state": "bull", "confidence": 0.7})

    assert result["portfolio_returns"].index.min() > portfolio_weights.index.min()
    for key in ["total_return", "sharpe_ratio", "sortino_ratio", "max_drawdown", "calmar_ratio", "turnover"]:
        assert key in result["metrics"]
    assert not result["equity_curve"].empty


def test_multi_factor_backtest_applies_transaction_cost_and_slippage():
    from evaluation.multi_factor_backtest import MultiFactorBacktest

    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    weights = pd.DataFrame(
        {
            "AAPL": [1.0, 0.0, 1.0, 0.0, 1.0],
            "TSLA": [0.0, 1.0, 0.0, 1.0, 0.0],
        },
        index=dates,
    )
    prices = pd.DataFrame(
        {
            "AAPL": [100, 102, 104, 106, 108],
            "TSLA": [100, 101, 102, 103, 104],
        },
        index=dates,
    )

    gross = MultiFactorBacktest(transaction_cost_bps=0.0, slippage_bps=0.0).run(weights, prices)
    net = MultiFactorBacktest(transaction_cost_bps=10.0, slippage_bps=5.0).run(weights, prices)

    assert net["metrics"]["total_cost"] > 0
    assert net["metrics"]["total_return"] < gross["metrics"]["total_return"]
    assert "gross_total_return" in net["metrics"]

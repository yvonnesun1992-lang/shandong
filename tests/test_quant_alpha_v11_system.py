from __future__ import annotations

import numpy as np
import pandas as pd


def sample_prices(days: int = 120, start: float = 100.0, step: float = 0.6, noise: float = 0.0) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=days, freq="D")
    close = start + np.arange(days) * step
    if noise:
        close = close + np.sin(np.arange(days) / 3) * noise
    return pd.DataFrame(
        {
            "datetime": dates,
            "open": close - 0.4,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": np.arange(days) + 1000,
        }
    )


def test_factor_engine_calculates_alpha_features_without_nan():
    from feature_engine.factors import calculate_factors

    factors = calculate_factors(sample_prices(days=120, step=0.5, noise=1.0))
    expected = {
        "momentum_5d",
        "momentum_20d",
        "momentum_60d",
        "zscore_price",
        "distance_to_ma",
        "bollinger_position",
        "realized_vol_5d",
        "realized_vol_20d",
        "volatility_regime",
        "ma_slope",
        "trend_strength",
        "adx_proxy",
    }

    assert expected <= set(factors.columns)
    assert not factors[list(expected)].tail(20).isna().any().any()
    assert factors["momentum_20d"].iloc[-1] > 0
    assert factors["trend_strength"].iloc[-1] >= 0


def test_regime_detector_identifies_bull_bear_and_sideways():
    from regime.regime_detector import RegimeDetector

    detector = RegimeDetector()
    bull = detector.detect(sample_prices(days=120, step=0.8, noise=0.2))
    bear = detector.detect(sample_prices(days=120, step=-0.8, noise=3.0))
    sideways = detector.detect(sample_prices(days=120, step=0.0, noise=0.4))

    assert bull["state"] == "bull"
    assert bear["state"] == "bear"
    assert sideways["state"] == "sideways"
    for result in [bull, bear, sideways]:
        assert 0 <= result["confidence"] <= 1


def test_strategy_ensemble_votes_and_adjusts_by_regime():
    from strategies.ensemble import StrategyEnsemble

    ensemble = StrategyEnsemble(vote_threshold=0.15)
    bull_signal = ensemble.generate_signal(sample_prices(days=120, step=0.8), "AAPL", {"state": "bull", "confidence": 0.9})
    bear_signal = ensemble.generate_signal(sample_prices(days=120, step=-0.8, noise=2.0), "AAPL", {"state": "bear", "confidence": 0.9})
    sideways_signal = ensemble.generate_signal(sample_prices(days=120, step=0.0, noise=0.2), "AAPL", {"state": "sideways", "confidence": 0.8})

    assert bull_signal["action"] == "BUY"
    assert bear_signal["action"] in {"SELL", "HOLD", "BUY"}
    assert sideways_signal["action"] in {"BUY", "SELL", "HOLD"}
    assert bull_signal["weights"]["momentum"] > bull_signal["weights"]["mean_reversion"]
    assert abs(sum(bull_signal["weights"].values()) - 1.0) < 1e-9
    assert -1 <= bull_signal["vote_score"] <= 1


def test_risk_engine_enforces_position_drawdown_and_volatility_controls():
    from risk.risk_engine import RiskEngine

    engine = RiskEngine(max_position_per_asset=0.10, max_drawdown=0.10, high_volatility_threshold=0.02)
    decision = engine.evaluate_order(
        symbol="AAPL",
        action="BUY",
        desired_value=50_000,
        portfolio_value=100_000,
        current_positions={"AAPL": 5_000},
        equity_curve=pd.Series([100_000, 98_000, 86_000]),
        volatility=0.05,
    )

    assert decision["approved_value"] <= 5_000
    assert decision["exposure_multiplier"] < 1
    assert decision["risk_score"] >= 50
    assert "max_position_per_asset" in decision["reasons"]
    assert "drawdown_control" in decision["reasons"]
    assert "volatility_deleveraging" in decision["reasons"]


def test_portfolio_optimizer_normalizes_weights_by_signal_volatility_and_regime():
    from portfolio.optimizer import PortfolioOptimizer

    optimizer = PortfolioOptimizer(max_weight=0.7)
    weights = optimizer.allocate(
        signals=[
            {"symbol": "AAPL", "action": "BUY", "strength": 0.9},
            {"symbol": "TSLA", "action": "BUY", "strength": 0.5},
            {"symbol": "NVDA", "action": "SELL", "strength": 0.8},
        ],
        volatility={"AAPL": 0.15, "TSLA": 0.30, "NVDA": 0.10},
        regime={"state": "bull", "confidence": 0.8},
    )

    assert set(weights) == {"AAPL", "TSLA"}
    assert all(0 <= value <= 0.7 for value in weights.values())
    assert abs(sum(weights.values()) - 1.0) < 1e-9
    assert weights["AAPL"] >= weights["TSLA"]


def test_backtest_v11_reports_regime_contribution_and_risk_metrics():
    from backtest.engine import BacktestEngine
    from strategies.ensemble import StrategyEnsemble

    result = BacktestEngine(initial_cash=100_000, trade_fraction=0.2).run(sample_prices(days=140, step=0.5, noise=1.0), StrategyEnsemble(), "AAPL")
    metrics = result["metrics"]

    for key in ["sortino_ratio", "calmar_ratio", "turnover", "risk_adjusted_return"]:
        assert key in metrics
    assert "regime_breakdown" in result
    assert "strategy_contribution" in result
    assert "risk_exposure" in result
    assert not result["equity_curve"]["total_equity"].isna().any()
    assert isinstance(result["strategy_contribution"], dict)


def test_visualization_v11_charts_return_figures():
    from visualization.chart import plot_regime_overlay, plot_risk_exposure, plot_strategy_contribution

    equity = pd.DataFrame(
        {
            "datetime": pd.date_range("2024-01-01", periods=6),
            "total_equity": [100, 102, 101, 105, 104, 108],
            "regime": ["sideways", "bull", "bull", "bull", "sideways", "bull"],
            "risk_score": [30, 35, 40, 42, 38, 36],
        }
    )

    assert plot_regime_overlay(equity) is not None
    assert plot_strategy_contribution({"ma": 0.04, "momentum": 0.06, "mean_reversion": -0.01}) is not None
    assert plot_risk_exposure(equity) is not None

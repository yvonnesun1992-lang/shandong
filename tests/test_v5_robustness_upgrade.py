from __future__ import annotations

import numpy as np
import pandas as pd


def test_default_robustness_universe_has_required_size_and_sectors():
    from quant_core_v5.robustness import DEFAULT_ROBUSTNESS_UNIVERSE

    symbols = [item["symbol"] for item in DEFAULT_ROBUSTNESS_UNIVERSE]
    sectors = {item["sector"] for item in DEFAULT_ROBUSTNESS_UNIVERSE}

    assert 30 <= len(symbols) <= 50
    assert len(symbols) == len(set(symbols))
    assert {"financial", "energy", "consumer", "healthcare"}.issubset(sectors)
    assert "technology" in sectors
    assert sum(1 for item in DEFAULT_ROBUSTNESS_UNIVERSE if item["cap"] == "mid") >= 5


def test_robustness_analysis_returns_required_sections_and_verdict():
    from quant_core_v5.robustness import run_robustness_analysis

    result = run_robustness_analysis(
        market_data=_market_data(["AAPL", "MSFT", "JPM", "XOM", "JNJ", "PG", "DE", "AFL"]),
        n_bootstrap=24,
        perturbation_pct=0.10,
        random_seed=7,
    )

    assert result["version"] == "V5.0-alpha-system"
    assert "multi_asset_performance" in result
    assert "regime_breakdown" in result
    assert "stability_metrics" in result
    assert "monte_carlo" in result
    assert "risk_assessment" in result
    assert set(result["regime_breakdown"]) == {
        "bull",
        "bear",
        "sideways",
        "high_volatility",
        "low_volatility",
    }
    for metrics in result["regime_breakdown"].values():
        assert {"return", "sharpe", "drawdown"}.issubset(metrics)
    assert result["stability_metrics"]["perturbation_pct"] == 0.10
    assert "stability_score" in result["stability_metrics"]
    assert {"alpha_confidence_interval", "worst_case_drawdown", "median_sharpe"}.issubset(result["monte_carlo"])
    assert result["risk_assessment"]["alpha_stability"] in {"HIGH", "MEDIUM", "LOW"}
    assert result["risk_assessment"]["overfitting_risk"] in {"HIGH", "MEDIUM", "LOW"}
    assert result["risk_assessment"]["production_readiness"] in {"YES", "NO"}
    assert result["audit"]["broker_connection"] is False
    assert result["audit"]["real_trading"] is False
    assert result["audit"]["core_alpha_formula_changed"] is False


def test_robustness_report_contains_required_risk_summary():
    from quant_core_v5.robustness import format_robustness_report, run_robustness_analysis

    result = run_robustness_analysis(
        market_data=_market_data(["AAPL", "MSFT", "JPM", "XOM", "JNJ", "PG", "DE", "AFL"]),
        n_bootstrap=16,
        random_seed=11,
    )
    report = format_robustness_report(result)

    assert "V5 Robustness Report" in report
    assert "Multi-Asset Performance" in report
    assert "Regime Breakdown" in report
    assert "Stability Metrics" in report
    assert "Monte Carlo / Bootstrap" in report
    assert "Overfitting risk score" in report
    assert "No broker connection" in report
    assert "No real trading" in report


def _market_data(symbols: list[str], days: int = 220) -> dict[str, pd.DataFrame]:
    return {symbol: _frame(i, days) for i, symbol in enumerate(symbols)}


def _frame(offset: int, days: int) -> pd.DataFrame:
    dates = pd.date_range("2022-01-01", periods=days, freq="D")
    trend = 100 + np.arange(days) * (0.03 + offset * 0.002)
    cycle = np.sin(np.arange(days) / (8 + offset % 3)) * (1.5 + offset * 0.05)
    drawdown_patch = np.where((np.arange(days) > 95) & (np.arange(days) < 125), -3.5 - offset * 0.1, 0)
    close = trend + cycle + drawdown_patch
    return pd.DataFrame(
        {
            "datetime": dates,
            "open": close - 0.2,
            "high": close + 0.8,
            "low": close - 0.8,
            "close": close,
            "volume": 1_000_000 + np.arange(days) * (10 + offset),
        }
    )

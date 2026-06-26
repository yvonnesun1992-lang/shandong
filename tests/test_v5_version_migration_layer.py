from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def test_version_migration_docs_exist_and_map_legacy_versions():
    migration = Path("docs/VERSION_MIGRATION_MAP.md")
    comparison = Path("docs/V1_to_V5_COMPARISON.md")

    assert migration.exists()
    assert comparison.exists()

    text = migration.read_text(encoding="utf-8")
    assert "V1.0 -> Paper Trading Core" in text
    assert "V1.1 -> Risk + Multi Strategy" in text
    assert "V1.2 -> Factor Research System" in text
    assert "V1.3 -> Multi-Factor Alpha System" in text
    assert "V5.0-alpha-system" in text

    comparison_text = comparison.read_text(encoding="utf-8")
    assert "V1 is a legacy research system" in comparison_text
    assert "V5 is the current alpha engine system" in comparison_text


def test_quant_core_v5_structure_and_entrypoints_are_available():
    from quant_core_v5.main import run_alpha_model, run_factor_pipeline, run_portfolio

    factor_matrices, price_matrix = _sample_inputs()
    factor_result = run_factor_pipeline(factor_matrices=factor_matrices, price_matrix=price_matrix)
    alpha_result = run_alpha_model(factor_matrices=factor_matrices, ic_results=factor_result["ic_results"])
    portfolio_result = run_portfolio(alpha_scores=alpha_result["alpha_scores"], price_matrix=price_matrix)

    assert {"ic_results", "factor_weights", "adjusted_factor_weights"} <= set(factor_result)
    assert not alpha_result["alpha_scores"].empty
    assert not portfolio_result["weights"].empty
    assert "metrics" in portfolio_result["backtest"]
    assert portfolio_result["backtest"]["portfolio_returns"].index.min() > portfolio_result["weights"].index.min()


def test_v5_reuses_v13_logic_without_legacy_code_moves():
    from alpha_engine.alpha_model import AlphaModel as V13AlphaModel
    from quant_core_v5.alpha_engine.alpha_model import AlphaModel as V5AlphaModel
    from quant_core_v5.portfolio.optimizer import OptimizedAllocation

    assert issubclass(V5AlphaModel, V13AlphaModel)
    assert callable(OptimizedAllocation().construct)


def _sample_inputs() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    dates = pd.date_range("2024-01-01", periods=16, freq="D")
    factors = {
        "momentum_20d": pd.DataFrame(
            {
                "AAPL": np.linspace(-0.5, 1.0, len(dates)),
                "TSLA": np.linspace(0.3, -0.2, len(dates)),
                "NVDA": np.sin(np.arange(len(dates)) / 3),
            },
            index=dates,
        ),
        "trend_strength": pd.DataFrame(
            {
                "AAPL": np.linspace(0.2, 0.8, len(dates)),
                "TSLA": np.linspace(0.4, 0.2, len(dates)),
                "NVDA": np.linspace(0.1, 0.6, len(dates)),
            },
            index=dates,
        ),
    }
    prices = pd.DataFrame(
        {
            "AAPL": 100 + np.arange(len(dates)) * 0.5,
            "TSLA": 90 + np.arange(len(dates)) * 0.2,
            "NVDA": 70 + np.arange(len(dates)) * 0.4,
        },
        index=dates,
    )
    return factors, prices

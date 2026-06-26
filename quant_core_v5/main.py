from __future__ import annotations

import pandas as pd

from quant_core_v5 import VERSION
from quant_core_v5.alpha_engine.alpha_model import AlphaModel
from quant_core_v5.factor_engine.scoring import score_factor_set
from quant_core_v5.portfolio.optimizer import OptimizedAllocation
from quant_core_v5.regime.regime_adjuster import RegimeAdjuster
from quant_core_v5.evaluation.backtest import MultiFactorBacktest


def run_factor_pipeline(
    factor_matrices: dict[str, pd.DataFrame],
    price_matrix: pd.DataFrame,
    regime: dict | None = None,
    forward_days: int = 1,
) -> dict:
    scoring = score_factor_set(factor_matrices=factor_matrices, price_matrix=price_matrix, forward_days=forward_days)
    adjusted = RegimeAdjuster().adjust(scoring["factor_weights"], regime or {"state": "sideways", "confidence": 0.0})
    return {
        "version": VERSION,
        "ic_results": scoring["ic_results"],
        "factor_weights": scoring["factor_weights"],
        "adjusted_factor_weights": adjusted,
    }


def run_alpha_model(
    factor_matrices: dict[str, pd.DataFrame],
    ic_results: list[dict] | None = None,
    factor_weights: dict[str, float] | None = None,
    regime: dict | None = None,
) -> dict:
    if factor_weights is None:
        from weighting.factor_weighting import compute_factor_weights

        factor_weights = compute_factor_weights(ic_results or [])
    adjusted = RegimeAdjuster().adjust(factor_weights, regime or {"state": "sideways", "confidence": 0.0})
    alpha_scores = AlphaModel().build_alpha_scores(factor_matrices=factor_matrices, factor_weights=adjusted)
    return {"version": VERSION, "factor_weights": adjusted, "alpha_scores": alpha_scores}


def run_portfolio(
    alpha_scores: pd.DataFrame,
    price_matrix: pd.DataFrame,
    max_weight_per_asset: float = 0.40,
    regime: dict | None = None,
    transaction_cost_bps: float = 0.0,
    slippage_bps: float = 0.0,
) -> dict:
    weights = OptimizedAllocation(max_weight_per_asset=max_weight_per_asset).construct(alpha_scores)
    backtest = MultiFactorBacktest(transaction_cost_bps=transaction_cost_bps, slippage_bps=slippage_bps).run(
        portfolio_weights=weights,
        price_matrix=price_matrix,
        regime=regime or {"state": "sideways", "confidence": 0.0},
    )
    return {"version": VERSION, "weights": weights, "backtest": backtest}

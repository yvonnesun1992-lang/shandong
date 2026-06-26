from __future__ import annotations

import pandas as pd

from factor_engine.factor_builder import FactorBuilder
from quant_core_v5 import VERSION
from quant_core_v5.main import run_alpha_model, run_factor_pipeline, run_portfolio


DEFAULT_FACTORS = ["momentum_20d", "trend_strength", "breakout_strength"]


def build_factor_matrices_from_market_data(
    market_data: dict[str, pd.DataFrame],
    factors: list[str] | None = None,
) -> dict:
    builder = FactorBuilder()
    selected_factors = factors or DEFAULT_FACTORS
    factor_matrices = {
        factor: builder.build_factor_matrix(market_data, factor)
        for factor in selected_factors
    }
    price_matrix = builder.build_price_matrix(market_data)
    return {
        "version": VERSION,
        "factor_matrices": factor_matrices,
        "price_matrix": price_matrix,
        "factors": selected_factors,
    }


def run_alpha_pipeline_from_market_data(
    market_data: dict[str, pd.DataFrame],
    factors: list[str] | None = None,
    regime: dict | None = None,
    max_weight_per_asset: float = 0.40,
    forward_days: int = 1,
    transaction_cost_bps: float = 0.0,
    slippage_bps: float = 0.0,
) -> dict:
    prepared = build_factor_matrices_from_market_data(market_data, factors=factors)
    factor = run_factor_pipeline(
        factor_matrices=prepared["factor_matrices"],
        price_matrix=prepared["price_matrix"],
        regime=regime,
        forward_days=forward_days,
    )
    alpha = run_alpha_model(
        factor_matrices=prepared["factor_matrices"],
        factor_weights=factor["adjusted_factor_weights"],
        regime=regime,
    )
    portfolio = run_portfolio(
        alpha_scores=alpha["alpha_scores"],
        price_matrix=prepared["price_matrix"],
        max_weight_per_asset=max_weight_per_asset,
        regime=regime,
        transaction_cost_bps=transaction_cost_bps,
        slippage_bps=slippage_bps,
    )
    return {
        "version": VERSION,
        "factor": factor,
        "alpha": alpha,
        "portfolio": portfolio,
        "summary": _summary(portfolio),
        "safety": _safety_boundary(),
    }


def _summary(portfolio: dict) -> dict:
    returns = portfolio["backtest"]["portfolio_returns"]
    return {
        "no_broker_connection": True,
        "causal_backtest": bool(not returns.empty and returns.index.min() > portfolio["weights"].index.min()),
        "number_of_return_observations": int(len(returns)),
        "metrics": portfolio["backtest"]["metrics"],
    }


def _safety_boundary() -> dict:
    return {
        "broker_connection": False,
        "real_trading": False,
        "auto_order_routing": False,
        "external_ai_api": False,
        "real_money_execution": False,
    }

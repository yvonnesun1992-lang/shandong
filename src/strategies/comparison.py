from __future__ import annotations

import pandas as pd

from src.backtest.portfolio_backtest import run_portfolio_backtest


RANKING_COLUMNS = [
    "preset_name",
    "total_return",
    "annualized_return",
    "max_drawdown",
    "number_of_trades",
    "final_portfolio_value",
]


# V1.17 only compares local research presets through the existing backtest engine.
def _preset_parameters(preset: dict) -> dict:
    return {
        "max_position_pct": float(preset.get("max_position_pct", 0.15)),
        "rebalance_frequency": str(preset.get("rebalance_frequency", "monthly")),
        "min_score_to_buy": int(preset.get("min_score_to_buy", 80)),
        "min_score_to_hold": int(preset.get("min_score_to_hold", 60)),
    }


def _ranking_row(preset_name: str, summary: dict) -> dict:
    return {
        "preset_name": preset_name,
        "total_return": summary.get("total_return"),
        "annualized_return": summary.get("annualized_return"),
        "max_drawdown": summary.get("max_drawdown"),
        "number_of_trades": summary.get("number_of_trades"),
        "final_portfolio_value": summary.get("final_portfolio_value"),
    }


def compare_strategy_presets(
    presets: dict[str, dict],
    price_data: dict[str, pd.DataFrame],
    initial_cash: float = 100000.0,
) -> dict:
    """Compare local strategy presets by running existing portfolio backtests."""
    if initial_cash <= 0:
        raise ValueError("initial_cash must be positive.")
    if not presets:
        raise ValueError("presets must contain at least one strategy preset.")
    if not price_data:
        raise ValueError("price_data must contain at least one symbol.")

    results: dict[str, dict] = {}
    failed_presets: list[dict] = []
    ranking_rows: list[dict] = []

    for preset_name, preset in presets.items():
        try:
            parameters = _preset_parameters(preset)
            backtest_result = run_portfolio_backtest(
                price_data,
                initial_cash=float(initial_cash),
                max_position_pct=parameters["max_position_pct"],
                rebalance_frequency=parameters["rebalance_frequency"],
                min_score_to_buy=parameters["min_score_to_buy"],
                min_score_to_hold=parameters["min_score_to_hold"],
            )
            summary = backtest_result["summary"]
            results[preset_name] = {
                "summary": summary,
                "equity_curve": backtest_result["equity_curve"],
                "trades": backtest_result["trades"],
            }
            ranking_rows.append(_ranking_row(preset_name, summary))
        except Exception as error:
            failed_presets.append({"name": preset_name, "error": str(error)})

    ranking = pd.DataFrame(ranking_rows, columns=RANKING_COLUMNS)
    if not ranking.empty:
        ranking = ranking.sort_values("total_return", ascending=False, na_position="last").reset_index(drop=True)

    return {
        "results": results,
        "failed_presets": failed_presets,
        "ranking": ranking,
    }

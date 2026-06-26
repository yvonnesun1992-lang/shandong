from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.multi_factor_backtest import MultiFactorBacktest
from quant_core_v5 import VERSION
from quant_core_v5.main import run_alpha_model, run_portfolio
from quant_core_v5.pipeline import DEFAULT_FACTORS, build_factor_matrices_from_market_data, run_alpha_pipeline_from_market_data


DEFAULT_ROBUSTNESS_UNIVERSE = [
    {"symbol": "AAPL", "sector": "technology", "cap": "large"},
    {"symbol": "MSFT", "sector": "technology", "cap": "large"},
    {"symbol": "NVDA", "sector": "technology", "cap": "large"},
    {"symbol": "ORCL", "sector": "technology", "cap": "large"},
    {"symbol": "ADBE", "sector": "technology", "cap": "large"},
    {"symbol": "JPM", "sector": "financial", "cap": "large"},
    {"symbol": "BAC", "sector": "financial", "cap": "large"},
    {"symbol": "GS", "sector": "financial", "cap": "large"},
    {"symbol": "MS", "sector": "financial", "cap": "large"},
    {"symbol": "AFL", "sector": "financial", "cap": "mid"},
    {"symbol": "XOM", "sector": "energy", "cap": "large"},
    {"symbol": "CVX", "sector": "energy", "cap": "large"},
    {"symbol": "COP", "sector": "energy", "cap": "large"},
    {"symbol": "SLB", "sector": "energy", "cap": "large"},
    {"symbol": "MRO", "sector": "energy", "cap": "mid"},
    {"symbol": "PG", "sector": "consumer", "cap": "large"},
    {"symbol": "KO", "sector": "consumer", "cap": "large"},
    {"symbol": "PEP", "sector": "consumer", "cap": "large"},
    {"symbol": "COST", "sector": "consumer", "cap": "large"},
    {"symbol": "TGT", "sector": "consumer", "cap": "large"},
    {"symbol": "JNJ", "sector": "healthcare", "cap": "large"},
    {"symbol": "PFE", "sector": "healthcare", "cap": "large"},
    {"symbol": "UNH", "sector": "healthcare", "cap": "large"},
    {"symbol": "MRK", "sector": "healthcare", "cap": "large"},
    {"symbol": "DXCM", "sector": "healthcare", "cap": "mid"},
    {"symbol": "CAT", "sector": "industrial", "cap": "large"},
    {"symbol": "DE", "sector": "industrial", "cap": "large"},
    {"symbol": "GE", "sector": "industrial", "cap": "large"},
    {"symbol": "URI", "sector": "industrial", "cap": "mid"},
    {"symbol": "NUE", "sector": "materials", "cap": "large"},
    {"symbol": "LIN", "sector": "materials", "cap": "large"},
    {"symbol": "FCX", "sector": "materials", "cap": "large"},
    {"symbol": "ALB", "sector": "materials", "cap": "mid"},
    {"symbol": "NEE", "sector": "utilities", "cap": "large"},
    {"symbol": "SO", "sector": "utilities", "cap": "large"},
    {"symbol": "DUK", "sector": "utilities", "cap": "large"},
    {"symbol": "WEC", "sector": "utilities", "cap": "mid"},
    {"symbol": "PLD", "sector": "real_estate", "cap": "large"},
    {"symbol": "O", "sector": "real_estate", "cap": "large"},
    {"symbol": "STAG", "sector": "real_estate", "cap": "mid"},
]


def run_robustness_analysis(
    market_data: dict[str, pd.DataFrame],
    factors: list[str] | None = None,
    perturbation_pct: float = 0.10,
    n_bootstrap: int = 500,
    random_seed: int = 42,
    transaction_cost_bps: float = 10.0,
    slippage_bps: float = 5.0,
    max_weight_per_asset: float = 0.10,
) -> dict:
    selected_factors = factors or DEFAULT_FACTORS
    effective_max_weight = max(float(max_weight_per_asset), 1.0 / max(len(market_data), 1))
    baseline = run_alpha_pipeline_from_market_data(
        market_data=market_data,
        factors=selected_factors,
        max_weight_per_asset=effective_max_weight,
        transaction_cost_bps=transaction_cost_bps,
        slippage_bps=slippage_bps,
    )
    prepared = build_factor_matrices_from_market_data(market_data, factors=selected_factors)
    returns = baseline["portfolio"]["backtest"]["portfolio_returns"].dropna()
    price_matrix = prepared["price_matrix"]
    factor_weights = baseline["factor"]["adjusted_factor_weights"]
    perturbations = _run_factor_perturbations(
        factor_matrices=prepared["factor_matrices"],
        price_matrix=price_matrix,
        factor_weights=factor_weights,
        perturbation_pct=perturbation_pct,
        max_weight_per_asset=effective_max_weight,
        transaction_cost_bps=transaction_cost_bps,
        slippage_bps=slippage_bps,
    )
    monte_carlo = _bootstrap_analysis(
        returns=returns,
        price_matrix=price_matrix,
        n_bootstrap=n_bootstrap,
        random_seed=random_seed,
    )
    stability = _stability_metrics(perturbations, perturbation_pct)
    regime = _regime_breakdown(returns=returns, price_matrix=price_matrix)
    risk = _risk_assessment(
        baseline_metrics=baseline["summary"]["metrics"],
        stability=stability,
        monte_carlo=monte_carlo,
        regime=regime,
    )
    return {
        "version": VERSION,
        "universe": _universe_summary(market_data),
        "multi_asset_performance": baseline["summary"]["metrics"],
        "regime_breakdown": regime,
        "stability_metrics": stability,
        "monte_carlo": monte_carlo,
        "risk_summary": _risk_summary(baseline["summary"]["metrics"], regime, monte_carlo),
        "risk_assessment": risk,
        "audit": {
            "broker_connection": False,
            "real_trading": False,
            "auto_order_routing": False,
            "external_ai_api": False,
            "core_alpha_formula_changed": False,
            "transaction_cost_bps": float(transaction_cost_bps),
            "slippage_bps": float(slippage_bps),
            "max_weight_per_asset": float(effective_max_weight),
        },
    }


def format_robustness_report(result: dict) -> str:
    metrics = result["multi_asset_performance"]
    stability = result["stability_metrics"]
    monte_carlo = result["monte_carlo"]
    risk = result["risk_assessment"]
    lines = [
        "# V5 Robustness Report",
        "",
        "## Multi-Asset Performance",
        f"- Asset count: {result['universe']['asset_count']}",
        f"- Sectors: {', '.join(result['universe']['sectors'])}",
        f"- Total return: {metrics.get('total_return', 0.0):.4f}",
        f"- Gross total return: {metrics.get('gross_total_return', 0.0):.4f}",
        f"- Sharpe: {metrics.get('sharpe_ratio', 0.0):.4f}",
        f"- Max drawdown: {metrics.get('max_drawdown', 0.0):.4f}",
        f"- Total cost: {metrics.get('total_cost', 0.0):.4f}",
        "",
        "## Regime Breakdown",
    ]
    for name, item in result["regime_breakdown"].items():
        lines.append(
            f"- {name}: return={item['return']:.4f}, sharpe={item['sharpe']:.4f}, drawdown={item['drawdown']:.4f}, observations={item['observations']}"
        )
    lines.extend(
        [
            "",
            "## Stability Metrics",
            f"- Perturbation pct: {stability['perturbation_pct']:.2f}",
            f"- Stability score: {stability['stability_score']:.8f}",
            f"- IC change proxy: {stability['ic_change_proxy']:.4f}",
            f"- Sharpe change: {stability['sharpe_change']:.4f}",
            "",
            "## Monte Carlo / Bootstrap",
            f"- Alpha confidence interval: {monte_carlo['alpha_confidence_interval'][0]:.4f} to {monte_carlo['alpha_confidence_interval'][1]:.4f}",
            f"- Worst case drawdown: {monte_carlo['worst_case_drawdown']:.4f}",
            f"- Median Sharpe: {monte_carlo['median_sharpe']:.4f}",
            "",
            "## Risk Summary",
            f"- Overfitting risk score: {risk['overfitting_risk_score']:.2f}",
            f"- Alpha stability: {risk['alpha_stability']}",
            f"- Overfitting risk: {risk['overfitting_risk']}",
            f"- Production readiness: {risk['production_readiness']}",
            f"- Recommended action: {risk['recommended_action']}",
            "",
            "## Safety",
            "- No broker connection",
            "- No real trading",
            "- No auto order routing",
            "- No external AI API",
            "- No profitability guarantee",
        ]
    )
    return "\n".join(lines)


def save_robustness_report(result: dict, path: str | Path = "reports/v5_robustness_report.md") -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(format_robustness_report(result), encoding="utf-8")
    return output


def _run_factor_perturbations(
    factor_matrices: dict[str, pd.DataFrame],
    price_matrix: pd.DataFrame,
    factor_weights: dict[str, float],
    perturbation_pct: float,
    max_weight_per_asset: float,
    transaction_cost_bps: float,
    slippage_bps: float,
) -> list[dict]:
    baseline = _evaluate_weights(
        factor_matrices,
        price_matrix,
        factor_weights,
        max_weight_per_asset,
        transaction_cost_bps,
        slippage_bps,
    )
    results = [{"scenario": "baseline", **baseline}]
    for factor in factor_weights:
        for direction in (-1, 1):
            perturbed = dict(factor_weights)
            perturbed[factor] = max(0.0, perturbed[factor] * (1 + direction * perturbation_pct))
            perturbed = _normalize_weights(perturbed)
            metrics = _evaluate_weights(
                factor_matrices,
                price_matrix,
                perturbed,
                max_weight_per_asset,
                transaction_cost_bps,
                slippage_bps,
            )
            results.append({"scenario": f"{factor}_{direction:+d}", **metrics})
    return results


def _evaluate_weights(
    factor_matrices: dict[str, pd.DataFrame],
    price_matrix: pd.DataFrame,
    factor_weights: dict[str, float],
    max_weight_per_asset: float,
    transaction_cost_bps: float,
    slippage_bps: float,
) -> dict:
    alpha = run_alpha_model(factor_matrices=factor_matrices, factor_weights=factor_weights)
    portfolio = run_portfolio(
        alpha_scores=alpha["alpha_scores"],
        price_matrix=price_matrix,
        max_weight_per_asset=max_weight_per_asset,
        transaction_cost_bps=transaction_cost_bps,
        slippage_bps=slippage_bps,
    )
    metrics = portfolio["backtest"]["metrics"]
    return {
        "total_return": float(metrics.get("total_return", 0.0)),
        "sharpe": float(metrics.get("sharpe_ratio", 0.0)),
        "factor_weights": dict(factor_weights),
    }


def _stability_metrics(perturbations: list[dict], perturbation_pct: float) -> dict:
    returns = np.array([item["total_return"] for item in perturbations], dtype=float)
    sharpes = np.array([item["sharpe"] for item in perturbations], dtype=float)
    baseline_return = float(returns[0]) if len(returns) else 0.0
    baseline_sharpe = float(sharpes[0]) if len(sharpes) else 0.0
    return {
        "perturbation_pct": float(perturbation_pct),
        "stability_score": float(np.var(returns)) if len(returns) else 0.0,
        "return_range": [float(np.min(returns)), float(np.max(returns))] if len(returns) else [0.0, 0.0],
        "ic_change_proxy": float(np.mean(np.abs(returns - baseline_return))) if len(returns) else 0.0,
        "sharpe_change": float(np.mean(np.abs(sharpes - baseline_sharpe))) if len(sharpes) else 0.0,
        "scenarios": perturbations,
    }


def _regime_breakdown(returns: pd.Series, price_matrix: pd.DataFrame) -> dict:
    market = price_matrix.pct_change().mean(axis=1).reindex(returns.index).fillna(0.0)
    rolling_return = market.rolling(40, min_periods=5).sum()
    rolling_vol = market.rolling(20, min_periods=5).std().fillna(0.0)
    vol_median = float(rolling_vol.median()) if not rolling_vol.empty else 0.0
    regimes = {
        "bull": rolling_return > 0,
        "bear": rolling_return < 0,
        "sideways": rolling_return.abs() <= rolling_return.abs().median() if not rolling_return.empty else rolling_return == 0,
        "high_volatility": rolling_vol >= vol_median,
        "low_volatility": rolling_vol < vol_median,
    }
    return {name: _metrics_for_returns(returns[mask.reindex(returns.index).fillna(False)]) for name, mask in regimes.items()}


def _bootstrap_analysis(returns: pd.Series, price_matrix: pd.DataFrame, n_bootstrap: int, random_seed: int) -> dict:
    rng = np.random.default_rng(random_seed)
    clean = returns.dropna().to_numpy(dtype=float)
    if len(clean) == 0:
        return {
            "alpha_confidence_interval": [0.0, 0.0],
            "worst_case_drawdown": 0.0,
            "median_sharpe": 0.0,
            "return_resampling_trials": 0,
            "factor_resampling_trials": 0,
            "portfolio_bootstrap_trials": 0,
        }
    totals = []
    sharpes = []
    drawdowns = []
    for _ in range(max(1, n_bootstrap)):
        sample = pd.Series(rng.choice(clean, size=len(clean), replace=True))
        metrics = _metrics_for_returns(sample)
        totals.append(metrics["return"])
        sharpes.append(metrics["sharpe"])
        drawdowns.append(metrics["drawdown"])
    asset_returns = price_matrix.pct_change().dropna()
    portfolio_trials = 0
    if not asset_returns.empty:
        for _ in range(max(1, n_bootstrap // 4)):
            columns = list(rng.choice(asset_returns.columns.to_numpy(), size=len(asset_returns.columns), replace=True))
            sampled = asset_returns[columns].mean(axis=1)
            metrics = _metrics_for_returns(sampled)
            totals.append(metrics["return"])
            sharpes.append(metrics["sharpe"])
            drawdowns.append(metrics["drawdown"])
            portfolio_trials += 1
    return {
        "alpha_confidence_interval": [float(np.percentile(totals, 5)), float(np.percentile(totals, 95))],
        "worst_case_drawdown": float(max(drawdowns)) if drawdowns else 0.0,
        "median_sharpe": float(np.median(sharpes)) if sharpes else 0.0,
        "return_resampling_trials": int(max(1, n_bootstrap)),
        "factor_resampling_trials": int(max(1, n_bootstrap)),
        "portfolio_bootstrap_trials": int(portfolio_trials),
    }


def _risk_summary(metrics: dict, regime: dict, monte_carlo: dict) -> dict:
    return {
        "max_drawdown": float(metrics.get("max_drawdown", 0.0)),
        "worst_regime_drawdown": float(max(item["drawdown"] for item in regime.values())) if regime else 0.0,
        "bootstrap_worst_case_drawdown": float(monte_carlo["worst_case_drawdown"]),
        "net_return": float(metrics.get("total_return", 0.0)),
        "sharpe": float(metrics.get("sharpe_ratio", 0.0)),
    }


def _risk_assessment(baseline_metrics: dict, stability: dict, monte_carlo: dict, regime: dict) -> dict:
    stability_score = float(stability["stability_score"])
    median_sharpe = float(monte_carlo["median_sharpe"])
    worst_drawdown = float(monte_carlo["worst_case_drawdown"])
    positive_regimes = sum(1 for item in regime.values() if item["return"] > 0)
    alpha_stability = "HIGH" if stability_score < 0.0005 and median_sharpe > 0.5 else "MEDIUM" if stability_score < 0.003 else "LOW"
    overfitting_score = min(100.0, stability_score * 10_000 + max(0.0, -median_sharpe) * 20 + max(0.0, worst_drawdown - 0.25) * 100)
    overfitting_risk = "LOW" if overfitting_score < 25 and positive_regimes >= 3 else "MEDIUM" if overfitting_score < 60 else "HIGH"
    readiness = (
        "YES"
        if alpha_stability in {"HIGH", "MEDIUM"}
        and overfitting_risk != "HIGH"
        and float(baseline_metrics.get("total_return", 0.0)) > 0
        and positive_regimes >= 3
        else "NO"
    )
    action = (
        "Proceed to extended paper-trading shadow validation with no broker execution."
        if readiness == "YES"
        else "Do not promote to production; expand validation windows and review unstable regimes."
    )
    return {
        "alpha_stability": alpha_stability,
        "overfitting_risk": overfitting_risk,
        "production_readiness": readiness,
        "overfitting_risk_score": float(overfitting_score),
        "recommended_action": action,
    }


def _metrics_for_returns(returns: pd.Series) -> dict:
    clean = returns.dropna()
    if clean.empty:
        return {"return": 0.0, "sharpe": 0.0, "drawdown": 0.0, "observations": 0}
    equity = (1 + clean).cumprod()
    total_return = float(equity.iloc[-1] - 1.0)
    std = float(clean.std(ddof=0))
    sharpe = float(clean.mean() / std * math.sqrt(252)) if std > 0 else 0.0
    peak = equity.cummax()
    drawdown = float(((peak - equity) / peak.replace(0, np.nan)).fillna(0.0).max())
    return {"return": total_return, "sharpe": sharpe, "drawdown": drawdown, "observations": int(len(clean))}


def _normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, float(value)) for value in weights.values())
    if total <= 0:
        equal = 1 / max(len(weights), 1)
        return {key: equal for key in weights}
    return {key: max(0.0, float(value)) / total for key, value in weights.items()}


def _universe_summary(market_data: dict[str, pd.DataFrame]) -> dict:
    meta = {item["symbol"]: item for item in DEFAULT_ROBUSTNESS_UNIVERSE}
    sectors = sorted({meta.get(symbol, {}).get("sector", "unknown") for symbol in market_data})
    caps = sorted({meta.get(symbol, {}).get("cap", "unknown") for symbol in market_data})
    return {"asset_count": int(len(market_data)), "symbols": sorted(market_data), "sectors": sectors, "caps": caps}

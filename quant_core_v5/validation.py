from __future__ import annotations

from pathlib import Path

import pandas as pd

from evaluation.splits import train_test_split_time, walk_forward_splits
from quant_core_v5 import VERSION
from quant_core_v5.pipeline import run_alpha_pipeline_from_market_data


def run_validation_harness(
    market_data: dict[str, pd.DataFrame],
    factors: list[str] | None = None,
    train_ratio: float = 0.70,
    walk_forward_train_size: int = 120,
    walk_forward_test_size: int = 30,
    max_weight_per_asset: float = 0.40,
    transaction_cost_bps: float = 10.0,
    slippage_bps: float = 5.0,
    regime: dict | None = None,
) -> dict:
    index = _common_index(market_data)
    train_index, test_index = train_test_split_time(index, train_ratio=train_ratio)
    train_data = _slice_market_data(market_data, train_index)
    test_data = _slice_market_data(market_data, test_index)

    train_result = run_alpha_pipeline_from_market_data(
        market_data=train_data,
        factors=factors,
        regime=regime,
        max_weight_per_asset=max_weight_per_asset,
        transaction_cost_bps=transaction_cost_bps,
        slippage_bps=slippage_bps,
    )
    test_result = run_alpha_pipeline_from_market_data(
        market_data=test_data,
        factors=factors,
        regime=regime,
        max_weight_per_asset=max_weight_per_asset,
        transaction_cost_bps=transaction_cost_bps,
        slippage_bps=slippage_bps,
    )

    walk_results = []
    for split in walk_forward_splits(index, train_size=walk_forward_train_size, test_size=walk_forward_test_size):
        window_data = _slice_market_data(market_data, split["test_index"])
        if _min_rows(window_data) < 3:
            continue
        window_result = run_alpha_pipeline_from_market_data(
            market_data=window_data,
            factors=factors,
            regime=regime,
            max_weight_per_asset=max_weight_per_asset,
            transaction_cost_bps=transaction_cost_bps,
            slippage_bps=slippage_bps,
        )
        walk_results.append(
            {
                "train_period": _period(split["train_index"]),
                "test_period": _period(split["test_index"]),
                "metrics": window_result["summary"]["metrics"],
                "summary": window_result["summary"],
            }
        )

    result = {
        "version": VERSION,
        "train": _pack_period_result(train_index, train_result),
        "test": _pack_period_result(test_index, test_result),
        "walk_forward": walk_results,
        "audit": _audit_summary(test_result, walk_results, transaction_cost_bps, slippage_bps),
    }
    return result


def format_validation_report(result: dict) -> str:
    train_metrics = result["train"]["summary"]["metrics"]
    test_metrics = result["test"]["summary"]["metrics"]
    audit = result["audit"]
    lines = [
        "# V5 Alpha Validation Report",
        "",
        "## Train Period",
        f"- Period: {result['train']['period']['start']} to {result['train']['period']['end']}",
        f"- Total return: {train_metrics.get('total_return', 0.0):.4f}",
        f"- Gross total return: {train_metrics.get('gross_total_return', 0.0):.4f}",
        f"- Total cost: {train_metrics.get('total_cost', 0.0):.4f}",
        f"- Sharpe ratio: {train_metrics.get('sharpe_ratio', 0.0):.4f}",
        "",
        "## Test Period",
        f"- Period: {result['test']['period']['start']} to {result['test']['period']['end']}",
        f"- Total return: {test_metrics.get('total_return', 0.0):.4f}",
        f"- Gross total return: {test_metrics.get('gross_total_return', 0.0):.4f}",
        f"- Total cost: {test_metrics.get('total_cost', 0.0):.4f}",
        f"- Sharpe ratio: {test_metrics.get('sharpe_ratio', 0.0):.4f}",
        "",
        "## Walk-Forward",
        f"- Windows: {len(result['walk_forward'])}",
        f"- Profitable windows: {audit['profitable_walk_forward_windows']}",
        f"- Profitable window ratio: {audit['profitable_walk_forward_ratio']:.4f}",
        "",
        "## Commercial Gates",
        f"- Transaction cost bps: {audit['transaction_cost_bps']:.2f}",
        f"- Slippage bps: {audit['slippage_bps']:.2f}",
        f"- Profitable test period: {audit['profitable_test_period']}",
        f"- Causal backtest: {audit['causal_backtest']}",
        "- No broker connection",
        "- No real trading",
        "- No profitability guarantee",
    ]
    return "\n".join(lines)


def save_validation_report(result: dict, path: str | Path = "reports/v5_alpha_validation_report.md") -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(format_validation_report(result), encoding="utf-8")
    return output


def _common_index(market_data: dict[str, pd.DataFrame]) -> pd.DatetimeIndex:
    common = None
    for frame in market_data.values():
        dates = pd.DatetimeIndex(pd.to_datetime(frame["datetime"])).sort_values().unique()
        common = dates if common is None else common.intersection(dates)
    return pd.DatetimeIndex(common).sort_values() if common is not None else pd.DatetimeIndex([])


def _slice_market_data(market_data: dict[str, pd.DataFrame], index: pd.DatetimeIndex) -> dict[str, pd.DataFrame]:
    selected = set(pd.DatetimeIndex(index))
    result = {}
    for symbol, frame in market_data.items():
        data = frame.copy()
        data["datetime"] = pd.to_datetime(data["datetime"])
        result[symbol] = data[data["datetime"].isin(selected)].sort_values("datetime").reset_index(drop=True)
    return result


def _period(index: pd.DatetimeIndex) -> dict:
    ordered = pd.DatetimeIndex(index).sort_values()
    return {
        "start": str(ordered.min().date()) if len(ordered) else "",
        "end": str(ordered.max().date()) if len(ordered) else "",
        "days": int(len(ordered)),
    }


def _pack_period_result(index: pd.DatetimeIndex, result: dict) -> dict:
    return {
        "period": _period(index),
        "summary": result["summary"],
        "factor_weights": result["factor"]["adjusted_factor_weights"],
    }


def _audit_summary(test_result: dict, walk_results: list[dict], transaction_cost_bps: float, slippage_bps: float) -> dict:
    test_metrics = test_result["summary"]["metrics"]
    profitable_windows = sum(1 for item in walk_results if item["metrics"].get("total_return", 0.0) > 0)
    return {
        "broker_connection": False,
        "real_trading": False,
        "auto_order_routing": False,
        "transaction_cost_bps": float(transaction_cost_bps),
        "slippage_bps": float(slippage_bps),
        "causal_backtest": bool(test_result["summary"]["causal_backtest"]),
        "profitable_test_period": bool(test_metrics.get("total_return", 0.0) > 0),
        "profitable_walk_forward_windows": int(profitable_windows),
        "walk_forward_windows": int(len(walk_results)),
        "profitable_walk_forward_ratio": float(profitable_windows / len(walk_results)) if walk_results else 0.0,
    }


def _min_rows(market_data: dict[str, pd.DataFrame]) -> int:
    if not market_data:
        return 0
    return min(len(frame) for frame in market_data.values())

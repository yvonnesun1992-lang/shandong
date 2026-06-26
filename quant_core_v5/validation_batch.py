from __future__ import annotations

from pathlib import Path

import pandas as pd

from quant_core_v5 import VERSION
from quant_core_v5.validation import run_validation_harness


def run_validation_batch(
    universes: dict[str, dict[str, pd.DataFrame]],
    factors: list[str] | None = None,
    train_ratio: float = 0.70,
    walk_forward_train_size: int = 120,
    walk_forward_test_size: int = 30,
    max_weight_per_asset: float = 0.40,
    transaction_cost_bps: float = 10.0,
    slippage_bps: float = 5.0,
) -> dict:
    results = {}
    for name, market_data in universes.items():
        results[name] = run_validation_harness(
            market_data=market_data,
            factors=factors,
            train_ratio=train_ratio,
            walk_forward_train_size=walk_forward_train_size,
            walk_forward_test_size=walk_forward_test_size,
            max_weight_per_asset=max_weight_per_asset,
            transaction_cost_bps=transaction_cost_bps,
            slippage_bps=slippage_bps,
        )
    return {
        "version": VERSION,
        "universes": results,
        "summary": _batch_summary(results),
        "audit": {
            "broker_connection": False,
            "real_trading": False,
            "auto_order_routing": False,
            "transaction_cost_bps": float(transaction_cost_bps),
            "slippage_bps": float(slippage_bps),
        },
    }


def format_batch_report(result: dict) -> str:
    summary = result["summary"]
    lines = [
        "# V5 Multi-Universe Validation Report",
        "",
        "## Summary",
        f"- Universe count: {summary['universe_count']}",
        f"- Profitable test ratio: {summary['profitable_test_ratio']:.4f}",
        f"- Average test return: {summary['average_test_return']:.4f}",
        f"- Average walk-forward profitable ratio: {summary['average_walk_forward_profitable_ratio']:.4f}",
        "",
        "## Universes",
    ]
    for name, item in result["universes"].items():
        test_metrics = item["test"]["summary"]["metrics"]
        audit = item["audit"]
        lines.extend(
            [
                f"- {name}: test_return={test_metrics.get('total_return', 0.0):.4f}, "
                f"test_sharpe={test_metrics.get('sharpe_ratio', 0.0):.4f}, "
                f"walk_forward_ratio={audit.get('profitable_walk_forward_ratio', 0.0):.4f}",
            ]
        )
    lines.extend(
        [
            "",
            "## Safety",
            "- No broker connection",
            "- No real trading",
            "- No auto order routing",
            "- No profitability guarantee",
        ]
    )
    return "\n".join(lines)


def save_batch_report(result: dict, path: str | Path = "reports/v5_multi_universe_validation_report.md") -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(format_batch_report(result), encoding="utf-8")
    return output


def _batch_summary(results: dict[str, dict]) -> dict:
    if not results:
        return {
            "universe_count": 0,
            "profitable_test_ratio": 0.0,
            "average_test_return": 0.0,
            "average_walk_forward_profitable_ratio": 0.0,
        }
    test_returns = [item["test"]["summary"]["metrics"].get("total_return", 0.0) for item in results.values()]
    profitable = [value > 0 for value in test_returns]
    wf_ratios = [item["audit"].get("profitable_walk_forward_ratio", 0.0) for item in results.values()]
    return {
        "universe_count": int(len(results)),
        "profitable_test_ratio": float(sum(profitable) / len(profitable)),
        "average_test_return": float(sum(test_returns) / len(test_returns)),
        "average_walk_forward_profitable_ratio": float(sum(wf_ratios) / len(wf_ratios)),
    }

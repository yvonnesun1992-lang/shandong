from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.data_loader import DataLoader
from quant_core_v5.robustness import DEFAULT_ROBUSTNESS_UNIVERSE, run_robustness_analysis, save_robustness_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5 robustness validation without broker execution.")
    parser.add_argument("--start", default="2021-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--max-symbols", type=int, default=40)
    parser.add_argument("--bootstrap", type=int, default=500)
    parser.add_argument("--output", default="reports/v5_robustness_report.md")
    args = parser.parse_args()

    selected = DEFAULT_ROBUSTNESS_UNIVERSE[: max(30, min(args.max_symbols, len(DEFAULT_ROBUSTNESS_UNIVERSE)))]
    loader = DataLoader()
    market_data = {}
    warnings = []
    for item in selected:
        symbol = item["symbol"]
        try:
            market_data[symbol] = loader.get_history(symbol, start=args.start, end=args.end, use_cache=True)
        except Exception as exc:  # pragma: no cover - defensive CLI path
            warnings.append(f"{symbol}: {type(exc).__name__}")

    if len(market_data) < 30:
        print(f"ERROR: robustness validation requires at least 30 assets, loaded {len(market_data)}")
        if warnings:
            print("Warnings: " + "; ".join(warnings[:10]))
        return 1

    result = run_robustness_analysis(market_data=market_data, n_bootstrap=args.bootstrap)
    output = save_robustness_report(result, args.output)
    print(f"V5 robustness report written to {output}")
    print(f"Production readiness: {result['risk_assessment']['production_readiness']}")
    print(f"Alpha stability: {result['risk_assessment']['alpha_stability']}")
    print(f"Overfitting risk: {result['risk_assessment']['overfitting_risk']}")
    print("Broker connection: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.data_loader import DataLoader
from quant_core_v5.validation import run_validation_harness, save_validation_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5 alpha validation without broker execution.")
    parser.add_argument("--symbols", default="AAPL,MSFT,NVDA", help="Comma-separated symbols.")
    parser.add_argument("--start", default="2022-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--output", default="reports/v5_alpha_validation_report.md")
    args = parser.parse_args()

    loader = DataLoader()
    symbols = [symbol.strip().upper() for symbol in args.symbols.split(",") if symbol.strip()]
    market_data = {
        symbol: loader.get_history(symbol, start=args.start, end=args.end, use_cache=True)
        for symbol in symbols
    }
    result = run_validation_harness(market_data=market_data)
    output = save_validation_report(result, args.output)
    print(f"V5 validation report written to {output}")
    print(f"Profitable test period: {result['audit']['profitable_test_period']}")
    print("Broker connection: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

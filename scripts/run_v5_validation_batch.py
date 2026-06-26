from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.data_loader import DataLoader
from quant_core_v5.validation_batch import run_validation_batch, save_batch_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5 multi-universe validation without broker execution.")
    parser.add_argument(
        "--universes",
        default="mega:AAPL,MSFT,NVDA;defensive:JNJ,PG,KO",
        help="Semicolon-separated universe_name:SYMBOL,SYMBOL groups.",
    )
    parser.add_argument("--start", default="2021-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--output", default="reports/v5_multi_universe_validation_report.md")
    args = parser.parse_args()

    loader = DataLoader()
    universes = {}
    for group in args.universes.split(";"):
        if not group.strip():
            continue
        name, symbols_text = group.split(":", 1)
        symbols = [symbol.strip().upper() for symbol in symbols_text.split(",") if symbol.strip()]
        universes[name.strip()] = {
            symbol: loader.get_history(symbol, start=args.start, end=args.end, use_cache=True)
            for symbol in symbols
        }
    result = run_validation_batch(universes=universes)
    output = save_batch_report(result, args.output)
    print(f"V5 multi-universe validation report written to {output}")
    print(f"Profitable test ratio: {result['summary']['profitable_test_ratio']:.4f}")
    print("Broker connection: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

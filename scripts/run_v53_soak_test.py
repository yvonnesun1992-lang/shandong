from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.soak_test_runner import run_replay_soak_test, run_synthetic_soak_test


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.3 long-run paper trading soak test.")
    parser.add_argument("--mode", choices=["synthetic", "replay"], default="synthetic")
    parser.add_argument("--ticks", type=int, default=1000)
    parser.add_argument("--faults", action="store_true")
    parser.add_argument("--market-mode", default="trend", choices=["trend", "sideways", "volatile", "crash"])
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()

    if args.mode == "synthetic":
        result = run_synthetic_soak_test(
            ticks=args.ticks,
            output_dir=args.output_dir,
            faults=args.faults,
            market_mode=args.market_mode,
        )
    else:
        result = run_replay_soak_test(ticks=args.ticks, output_dir=args.output_dir, faults=args.faults)
    printable = {key: value for key, value in result.items() if key not in {"checkpoint_state", "final_state"}}
    print(json.dumps(printable, sort_keys=True))
    return 0 if result.get("final_verdict") in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime.live_alpha_report import generate_live_alpha_report
from runtime.live_paper_alpha_runner import run_live_paper_alpha_staging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V5.7 live alpha paper integration.")
    parser.add_argument("--mode", choices=["mock_live", "yfinance_polling"], default="mock_live")
    parser.add_argument("--ticks", type=int, default=100)
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.once:
        summary = run_live_paper_alpha_staging(mode=args.mode, max_ticks=1, dry_run_once=True)
        result = {"path": "reports/v5_7_live_alpha_signal_integration_report.md", "verdict": "WARNING" if summary.get("warnings") else "PASS", "summary": summary}
        generate_live_alpha_report(mode=args.mode, ticks=1)
    else:
        result = generate_live_alpha_report(mode=args.mode, ticks=args.ticks)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("verdict") == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())

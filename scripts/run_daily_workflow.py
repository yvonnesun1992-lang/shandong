from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.cn_data import get_cn_ohlcv
from src.data.us_data import get_us_ohlcv
from src.data.watchlist_manager import load_watchlist
from src.workflows.daily_workflow import run_daily_research_workflow
from src.workflows.run_log import save_workflow_run_log


def fetch_data(market: str, symbol: str):
    if market == "us":
        return get_us_ohlcv(symbol)
    if market == "cn":
        return get_cn_ohlcv(symbol)
    raise ValueError("market must be 'us' or 'cn'.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local daily research workflow.")
    parser.add_argument("--market", choices=["us", "cn"], required=True)
    parser.add_argument("--watchlist", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        symbols = load_watchlist(args.watchlist)
        result = run_daily_research_workflow(
            market=args.market,
            watchlist_name=args.watchlist,
            symbols=symbols,
            fetch_data_func=fetch_data,
        )
        saved_log = save_workflow_run_log(result)
    except Exception as error:
        print(f"Daily workflow failed: {error}", file=sys.stderr)
        return 1

    if not result["success"]:
        print(f"run_id: {saved_log['run_id']}")
        print(f"report_id: {result.get('report_id')}")
        print(f"success_count: {result['success_count']}")
        print(f"failed_count: {result['failed_count']}")
        print(f"elapsed_seconds: {result['elapsed_seconds']:.2f}")
        print(f"Daily workflow failed: {result.get('error', 'unknown error')}", file=sys.stderr)
        return 1

    print(f"run_id: {saved_log['run_id']}")
    print(f"report_id: {result['report_id']}")
    print(f"report_path: {result['report_path']}")
    print(f"success_count: {result['success_count']}")
    print(f"failed_count: {result['failed_count']}")
    print(f"elapsed_seconds: {result['elapsed_seconds']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

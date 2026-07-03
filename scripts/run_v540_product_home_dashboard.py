from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.v5_product_home_config import get_product_home_status
from product_home.backtest_summary import build_backtest_summary
from product_home.main_feature_cards import build_main_feature_cards
from product_home.paper_trading_summary import build_paper_trading_summary
from product_home.product_home_orchestrator import build_product_home_dashboard, summarize_product_home_dashboard
from product_home.product_home_safety_validator import build_product_home_safety_summary
from product_home.risk_boundary_summary import build_risk_boundary_summary
from product_home.runtime_visibility_summary import build_runtime_visibility_summary
from product_home.system_health_summary import build_system_health_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the V5.40 product home dashboard summary.")
    parser.add_argument("--check", choices=["health", "runtime", "paper", "backtest", "risk", "cards", "safety", "status"])
    args = parser.parse_args()

    if args.check == "health":
        payload = build_system_health_summary()
    elif args.check == "runtime":
        payload = build_runtime_visibility_summary()
    elif args.check == "paper":
        payload = build_paper_trading_summary()
    elif args.check == "backtest":
        payload = build_backtest_summary()
    elif args.check == "risk":
        payload = build_risk_boundary_summary()
    elif args.check == "cards":
        payload = {"feature_cards": build_main_feature_cards(), "product_home_only": True}
    elif args.check == "safety":
        payload = build_product_home_safety_summary()
    elif args.check == "status":
        payload = get_product_home_status()
    else:
        payload = summarize_product_home_dashboard(build_product_home_dashboard())

    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    verdict = payload.get("verdict", "PASS")
    return 1 if verdict == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())

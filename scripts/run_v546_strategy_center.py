from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_strategy_center_config import get_strategy_center_status
from strategy_center.strategy_card_model import build_strategy_cards
from strategy_center.strategy_catalog import build_strategy_catalog, list_strategy_categories
from strategy_center.strategy_center_orchestrator import build_strategy_center_dashboard
from strategy_center.strategy_center_report import generate_strategy_center_report
from strategy_center.strategy_center_safety_validator import build_strategy_center_safety_summary
from strategy_center.strategy_detail_model import build_strategy_detail
from strategy_center.strategy_education_copy import build_education_copy
from strategy_center.strategy_recommendation import build_strategy_recommendation_panel
from strategy_center.strategy_search import build_strategy_search_result


def build_payload(check: str) -> dict:
    if check == "catalog":
        return {"catalog": build_strategy_catalog(), "categories": list_strategy_categories(), "strategy_center_only": True}
    if check == "search":
        return build_strategy_search_result("小市值", {})
    if check == "recommendations":
        return build_strategy_recommendation_panel()
    if check == "cards":
        return {"cards": build_strategy_cards(build_strategy_catalog()), "strategy_center_only": True}
    if check == "detail":
        return build_strategy_detail("small_cap_momentum")
    if check == "education":
        return build_education_copy()
    if check == "safety":
        return build_strategy_center_safety_summary()
    if check == "report":
        return generate_strategy_center_report()
    dashboard = build_strategy_center_dashboard()
    generate_strategy_center_report()
    return dashboard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run V5.46 strategy center checks.")
    parser.add_argument("--check", choices=["summary", "catalog", "search", "recommendations", "cards", "detail", "education", "safety", "report"], default="summary")
    args = parser.parse_args(argv)
    payload = build_payload(args.check)
    payload = {**get_strategy_center_status(), **payload}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    if payload.get("verdict") == "FAIL" or payload.get("safe") is False:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

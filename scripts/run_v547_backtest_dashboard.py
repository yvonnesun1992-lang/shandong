from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtest_dashboard.backtest_action_panel import build_backtest_action_panel
from backtest_dashboard.backtest_chart_model import build_backtest_charts
from backtest_dashboard.backtest_conclusion_engine import build_backtest_conclusion
from backtest_dashboard.backtest_dashboard_orchestrator import build_backtest_dashboard
from backtest_dashboard.backtest_dashboard_report import generate_backtest_dashboard_report
from backtest_dashboard.backtest_dashboard_safety_validator import build_backtest_dashboard_safety_summary
from backtest_dashboard.backtest_result_model import build_backtest_advanced_metrics, build_backtest_core_metrics, build_backtest_result
from backtest_dashboard.backtest_risk_analysis import build_risk_analysis
from backtest_dashboard.backtest_summary_cards import build_advanced_metric_cards, build_core_metric_cards
from config.v5_backtest_dashboard_config import get_backtest_dashboard_status


def build_payload(check: str, strategy_id: str) -> dict:
    core_metrics = build_backtest_core_metrics(strategy_id)
    conclusion = build_backtest_conclusion(core_metrics)
    if check == "result":
        return build_backtest_result(strategy_id)
    if check == "conclusion":
        return conclusion
    if check == "metrics":
        return {"core_metric_cards": build_core_metric_cards(core_metrics), "advanced_metric_cards": build_advanced_metric_cards(build_backtest_advanced_metrics(strategy_id)), "backtest_dashboard_only": True}
    if check == "charts":
        return build_backtest_charts(strategy_id)
    if check == "risk":
        return build_risk_analysis(core_metrics)
    if check == "actions":
        return build_backtest_action_panel(strategy_id, conclusion)
    if check == "safety":
        return build_backtest_dashboard_safety_summary()
    if check == "report":
        return generate_backtest_dashboard_report(strategy_id)
    dashboard = build_backtest_dashboard(strategy_id)
    generate_backtest_dashboard_report(strategy_id)
    return dashboard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run V5.47 backtest dashboard checks.")
    parser.add_argument("--strategy", default="small_cap_momentum")
    parser.add_argument("--check", choices=["summary", "result", "conclusion", "metrics", "charts", "risk", "actions", "safety", "report"], default="summary")
    args = parser.parse_args(argv)
    payload = {**get_backtest_dashboard_status(), **build_payload(args.check, args.strategy)}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    if payload.get("verdict") == "FAIL" or payload.get("safe") is False:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

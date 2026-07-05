from __future__ import annotations

from backtest_dashboard.backtest_action_panel import build_backtest_action_panel
from backtest_dashboard.backtest_chart_model import build_backtest_charts
from backtest_dashboard.backtest_conclusion_engine import build_backtest_conclusion
from backtest_dashboard.backtest_dashboard_safety_validator import validate_backtest_dashboard_safety
from backtest_dashboard.backtest_result_model import build_backtest_advanced_metrics, build_backtest_core_metrics, build_backtest_metadata
from backtest_dashboard.backtest_risk_analysis import build_risk_analysis
from backtest_dashboard.backtest_summary_cards import build_advanced_metric_cards, build_core_metric_cards
from backtest_dashboard.metric_explanation_copy import build_metric_explanations


def build_backtest_dashboard(strategy_id: str) -> dict:
    metadata = build_backtest_metadata(strategy_id)
    core_metrics = build_backtest_core_metrics(strategy_id)
    advanced_metrics = build_backtest_advanced_metrics(strategy_id)
    conclusion = build_backtest_conclusion(core_metrics)
    risk = build_risk_analysis(core_metrics)
    dashboard = {
        "backtest_dashboard_ready": True,
        "strategy_id": strategy_id,
        "metadata": metadata,
        "conclusion": conclusion,
        "risk_analysis": risk,
        "core_metric_cards": build_core_metric_cards(core_metrics),
        "advanced_metric_cards": build_advanced_metric_cards(advanced_metrics),
        "charts": build_backtest_charts(strategy_id),
        "actions": build_backtest_action_panel(strategy_id, conclusion)["actions"],
        "metric_explanations": build_metric_explanations(),
        "warnings": [],
        "errors": [],
        "verdict": "PASS",
        "backtest_dashboard_only": True,
        "localhost_only": True,
        "paper_trading": True,
        "real_trading_enabled": False,
        "broker_connected": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "balance_read_enabled": False,
        "position_read_enabled": False,
        "order_preview_enabled": False,
        "order_submission_enabled": False,
        "real_money_enabled": False,
    }
    safety = validate_backtest_dashboard_safety(dashboard)
    dashboard["safety"] = safety
    if not safety["safe"]:
        dashboard["backtest_dashboard_ready"] = False
        dashboard["errors"] = safety["findings"]
        dashboard["verdict"] = "FAIL"
    return dashboard


def summarize_backtest_dashboard(result: dict | None = None) -> dict:
    result = result or build_backtest_dashboard("small_cap_momentum")
    return {
        "backtest_dashboard_ready": result["backtest_dashboard_ready"],
        "strategy_id": result["strategy_id"],
        "display_name": result["metadata"]["display_name"],
        "conclusion": result["conclusion"]["user_summary"],
        "risk_level": result["risk_analysis"]["risk_level"],
        "core_metric_count": len(result["core_metric_cards"]),
        "advanced_metric_count": len(result["advanced_metric_cards"]),
        "chart_count": len(result["charts"]) - 2 if "backtest_dashboard_only" in result["charts"] else len(result["charts"]),
        "action_count": len(result["actions"]),
        "verdict": result["verdict"],
        "warnings": result.get("warnings", []),
        "errors": result.get("errors", []),
        "backtest_dashboard_only": True,
        "localhost_only": True,
        "paper_trading": True,
        "real_trading_enabled": False,
    }

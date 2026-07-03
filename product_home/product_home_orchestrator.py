from __future__ import annotations

from product_home.backtest_summary import build_backtest_summary
from product_home.init import boundary
from product_home.main_feature_cards import build_main_feature_cards
from product_home.paper_trading_summary import build_paper_trading_summary
from product_home.product_home_safety_validator import validate_product_home_safety
from product_home.recent_activity_summary import build_recent_activity_summary
from product_home.risk_boundary_summary import build_risk_boundary_summary
from product_home.runtime_visibility_summary import build_runtime_visibility_summary
from product_home.system_health_summary import build_system_health_summary


def build_product_home_dashboard() -> dict:
    health = build_system_health_summary()
    runtime = build_runtime_visibility_summary()
    paper = build_paper_trading_summary()
    backtest = build_backtest_summary()
    risk = build_risk_boundary_summary()
    activity = build_recent_activity_summary()
    cards = build_main_feature_cards()
    warnings = health.get("warnings", []) + runtime.get("warnings", []) + activity.get("warnings", [])
    errors = health.get("errors", [])
    payload = {
        "product_home_ready": not errors,
        "system_health": health["system_health"],
        "runtime_visible": runtime["runtime_visible"],
        "system_health_summary": health,
        "runtime_visibility": runtime,
        "paper_trading_summary": paper,
        "backtest_summary": backtest,
        "risk_boundary_summary": risk,
        "recent_activity": activity,
        "feature_cards": cards,
        "warnings": warnings,
        "errors": errors,
        **boundary(),
    }
    safety = validate_product_home_safety(payload)
    payload["safety"] = safety
    payload["verdict"] = "FAIL" if errors or not safety["safe"] else "WARNING" if warnings else "PASS"
    return payload


def summarize_product_home_dashboard(result: dict) -> dict:
    return {
        "product_home_ready": result.get("product_home_ready", False),
        "system_health": result.get("system_health", "FAIL"),
        "runtime_visible": result.get("runtime_visible", False),
        "feature_card_count": len(result.get("feature_cards", [])),
        "warnings": result.get("warnings", []),
        "errors": result.get("errors", []),
        "verdict": result.get("verdict", "FAIL"),
        **boundary(),
    }

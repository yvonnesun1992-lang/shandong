from __future__ import annotations

from strategy_center.strategy_card_model import build_strategy_cards
from strategy_center.strategy_catalog import build_strategy_catalog, list_strategy_categories
from strategy_center.strategy_center_safety_validator import build_strategy_center_safety_summary
from strategy_center.strategy_education_copy import build_education_copy
from strategy_center.strategy_recommendation import build_strategy_recommendation_panel
from strategy_center.strategy_search import build_strategy_search_result


def build_strategy_center_dashboard() -> dict:
    catalog = build_strategy_catalog()
    recommendations = build_strategy_recommendation_panel()
    safety = build_strategy_center_safety_summary()
    errors = [] if safety["safe"] else safety["findings"]
    return {
        "strategy_center_ready": safety["safe"],
        "catalog": catalog,
        "categories": list_strategy_categories(),
        "recommended_strategies": recommendations["recommended_strategies"],
        "recommendation_panel": recommendations,
        "search": build_strategy_search_result("", {}),
        "strategy_cards": build_strategy_cards(catalog),
        "education": build_education_copy(),
        "safety": safety,
        "warnings": [],
        "errors": errors,
        "verdict": "PASS" if safety["safe"] else "FAIL",
        "strategy_center_only": True,
        "localhost_only": True,
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
        "paper_trading": True,
    }


def summarize_strategy_center(result: dict | None = None) -> dict:
    result = result or build_strategy_center_dashboard()
    return {
        "strategy_center_ready": result["strategy_center_ready"],
        "catalog_count": len(result["catalog"]),
        "category_count": len(result["categories"]),
        "recommended_count": len(result["recommended_strategies"]),
        "card_count": len(result["strategy_cards"]),
        "verdict": result["verdict"],
        "warnings": result.get("warnings", []),
        "errors": result.get("errors", []),
        "strategy_center_only": True,
        "localhost_only": True,
        "paper_trading": True,
    }

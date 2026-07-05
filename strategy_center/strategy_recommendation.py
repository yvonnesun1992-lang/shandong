from __future__ import annotations

from strategy_center.strategy_catalog import build_strategy_catalog


def _by_ids(ids: list[str]) -> list[dict]:
    catalog = {item["strategy_id"]: item for item in build_strategy_catalog()}
    return [catalog[item_id] for item_id in ids if item_id in catalog]


def recommend_strategies_for_beginner() -> list[dict]:
    return _by_ids(["csi300_enhanced", "dividend_low_vol", "blue_chip_value"])


def recommend_strategies_by_market(market_state: str) -> list[dict]:
    return [item for item in build_strategy_catalog() if item["suitable_market"] == market_state][:3]


def recommend_strategies_by_risk_preference(risk_preference: str) -> list[dict]:
    return [item for item in build_strategy_catalog() if item["risk_level"] == risk_preference][:3]


def build_strategy_recommendation_panel(profile: str = "beginner") -> dict:
    if profile == "steady":
        strategies = _by_ids(["dividend_low_vol", "bank_rotation", "low_valuation_select"])
        reason = "偏稳健：优先展示低波、红利和低估值策略。"
    elif profile == "advanced":
        strategies = _by_ids(["small_cap_momentum", "sector_rotation", "semiconductor_momentum"])
        reason = "进阶用户：可先用模拟交易观察更高波动策略。"
    else:
        strategies = recommend_strategies_for_beginner()
        reason = "新手默认：先从指数增强、红利低波和蓝筹低估值开始。"
    return {
        "recommended_strategies": strategies,
        "reason": reason,
        "risk_warning": "所有策略仅用于回测和模拟交易，不能直接进入真实交易。",
        "next_action": "run_backtest",
        "real_trading_enabled": False,
        "strategy_center_only": True,
    }

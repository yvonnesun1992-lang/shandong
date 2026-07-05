from __future__ import annotations

from strategy_center.strategy_catalog import build_strategy_catalog


SEARCH_ALIASES = {
    "小市值": ["小市值"],
    "动量": ["动量", "趋势"],
    "红利": ["红利"],
    "低波": ["低波"],
    "低估值": ["低估值", "蓝筹"],
    "银行": ["银行"],
    "半导体": ["半导体"],
    "指数增强": ["指数增强", "沪深300"],
    "稳健": ["稳健", "低波", "蓝筹"],
    "新手": ["新手"],
    "趋势": ["趋势", "动量"],
    "行业轮动": ["行业轮动"],
}


def search_strategies(query: str | None = None) -> list[dict]:
    query = (query or "").strip()
    catalog = build_strategy_catalog()
    if not query:
        return catalog
    terms = SEARCH_ALIASES.get(query, [query])
    result = []
    for item in catalog:
        haystack = " ".join(
            [
                item["display_name"],
                item["short_description"],
                item["beginner_explanation"],
                item["category"],
                item["strategy_type"],
                " ".join(item["tags"]),
            ]
        )
        if any(term.lower() in haystack.lower() for term in terms):
            result.append(item)
    return result


def filter_strategies(filters: dict | None = None) -> list[dict]:
    filters = {key: value for key, value in (filters or {}).items() if value not in {None, "", "all"}}
    result = build_strategy_catalog()
    for key, value in filters.items():
        if key in {
            "risk_level",
            "suitable_market",
            "strategy_type",
            "suitable_user",
            "category",
            "backtest_available",
            "paper_trading_available",
        }:
            result = [item for item in result if item.get(key) == value]
    return result


def rank_strategies_for_user(preference: dict | None = None) -> list[dict]:
    preference = preference or {}
    risk = preference.get("risk_level")
    user = preference.get("suitable_user")
    market = preference.get("suitable_market")
    scored = []
    for item in build_strategy_catalog():
        score = 0
        if risk and item["risk_level"] == risk:
            score += 3
        if user and item["suitable_user"] == user:
            score += 3
        if market and item["suitable_market"] == market:
            score += 2
        if item["backtest_available"]:
            score += 1
        if item["paper_trading_available"]:
            score += 1
        scored.append((score, item))
    return [item for _, item in sorted(scored, key=lambda pair: pair[0], reverse=True)]


def build_strategy_search_result(query: str | None = None, filters: dict | None = None) -> dict:
    searched = search_strategies(query)
    allowed_ids = {item["strategy_id"] for item in filter_strategies(filters)}
    results = [item for item in searched if item["strategy_id"] in allowed_ids]
    return {
        "query": query or "",
        "filters": filters or {},
        "results": results,
        "total": len(results),
        "strategy_center_only": True,
        "localhost_only": True,
    }

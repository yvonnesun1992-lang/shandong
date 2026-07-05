from __future__ import annotations


TYPE_COPY = {
    "value": "低估值策略会优先观察价格相对便宜、业务更稳的资产。",
    "growth": "成长策略会关注增长更快的公司，但波动也可能更高。",
    "momentum": "动量策略会观察近期更强的资产是否继续保持强势。",
    "dividend": "红利低波策略会偏向分红和波动更平缓的资产。",
    "index_enhancement": "指数增强策略以指数为基础，尝试做温和优化。",
    "sector_rotation": "行业轮动策略会观察不同板块热度的变化。",
}


def explain_strategy_type(strategy_type: str) -> str:
    return TYPE_COPY.get(strategy_type, "这类策略用于本地回测和模拟交易观察。")


def explain_risk_level(risk_level: str) -> str:
    if risk_level == "low":
        return "低风险代表模拟回撤相对更平缓，但不代表没有风险。"
    if risk_level == "high":
        return "高风险代表波动和回撤可能更大，建议只先用模拟交易观察。"
    return "中等风险代表收益和波动都需要一起观察。"


def explain_suitable_market(market: str) -> str:
    mapping = {
        "bull": "更适合上涨趋势较明确的市场。",
        "bear": "更适合防守或弱市观察。",
        "sideways": "更适合震荡市场，不依赖单边上涨。",
        "liquidity_driven": "更适合流动性较好、市场活跃的阶段。",
    }
    return mapping.get(market, "适合市场需要结合回测和模拟交易继续观察。")


def explain_backtest() -> str:
    return "回测是用历史数据模拟策略过去会怎样表现，普通用户可以先用它理解收益和风险。"


def explain_paper_trading() -> str:
    return "模拟交易是在本地用虚拟资金观察策略运行，不会使用真实资金。"


def explain_why_not_real_trading() -> str:
    return "不能直接上真实交易，因为真实交易需要券商、资金、人工审批和更严格风控，本阶段只做回测和模拟交易。"


def explain_max_drawdown() -> str:
    return "最大回撤表示从阶段高点到低点最多跌了多少，是普通用户理解风险的重要指标。"


def explain_win_rate() -> str:
    return "胜率表示历史样本中盈利交易或盈利阶段的比例，不等于未来一定盈利。"


def explain_sharpe() -> str:
    return "夏普比率用于粗略比较收益和波动，数值越高通常代表单位波动带来的收益更好。"


def build_education_copy() -> dict:
    return {
        "backtest": explain_backtest(),
        "paper_trading": explain_paper_trading(),
        "max_drawdown": explain_max_drawdown(),
        "win_rate": explain_win_rate(),
        "sharpe": explain_sharpe(),
        "small_cap": "小市值策略关注规模较小的公司，弹性可能更大，波动也可能更大。",
        "momentum": explain_strategy_type("momentum"),
        "dividend_low_vol": explain_strategy_type("dividend"),
        "why_not_real_trading": explain_why_not_real_trading(),
        "strategy_center_only": True,
    }

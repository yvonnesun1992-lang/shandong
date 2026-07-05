from __future__ import annotations


def explain_strategy_return() -> str:
    return "策略收益：策略在回测期间赚了多少。"


def explain_benchmark_return() -> str:
    return "基准收益：同期市场指数涨了多少。"


def explain_excess_return() -> str:
    return "超额收益：策略比市场多赚或少赚多少。"


def explain_annualized_return() -> str:
    return "年化收益：把回测收益换算成每年的平均表现。"


def explain_max_drawdown() -> str:
    return "最大回撤：最差的时候亏了多少，是普通投资者最需要先看的风险指标。"


def explain_win_rate() -> str:
    return "胜率：赚钱天数或交易次数占比。"


def explain_profit_loss_ratio() -> str:
    return "盈亏比：平均赚钱幅度和平均亏钱幅度的比较。"


def explain_sharpe() -> str:
    return "夏普比率：收益是否值得承担这些风险。"


def explain_alpha() -> str:
    return "Alpha：策略在扣除市场影响后额外贡献的收益。"


def explain_beta() -> str:
    return "Beta：策略跟随市场波动的程度。"


def explain_information_ratio() -> str:
    return "信息比率：策略相对基准的超额收益是否稳定。"


def explain_sortino() -> str:
    return "索提诺比率：更关注下跌风险后的收益质量。"


def explain_volatility() -> str:
    return "波动率：收益曲线起伏大小，越高代表体验越颠簸。"


def build_metric_explanations() -> dict:
    return {
        "策略收益": explain_strategy_return(),
        "基准收益": explain_benchmark_return(),
        "超额收益": explain_excess_return(),
        "年化收益": explain_annualized_return(),
        "最大回撤": explain_max_drawdown(),
        "胜率": explain_win_rate(),
        "盈亏比": explain_profit_loss_ratio(),
        "夏普比率": explain_sharpe(),
        "Alpha": explain_alpha(),
        "Beta": explain_beta(),
        "信息比率": explain_information_ratio(),
        "索提诺比率": explain_sortino(),
        "波动率": explain_volatility(),
        "backtest_dashboard_only": True,
        "real_trading_enabled": False,
    }

from __future__ import annotations

from backtest_dashboard.metric_explanation_copy import build_metric_explanations


def _percent(value: float) -> str:
    return f"{value:.1%}"


def _card(label: str, value: float, explanation: str, warning: str = "") -> dict:
    direction = "positive" if value > 0 else "negative" if value < 0 else "neutral"
    return {
        "label": label,
        "value": value,
        "display_value": _percent(value) if abs(value) < 3 else f"{value:.2f}",
        "direction": direction,
        "explanation": explanation,
        "user_friendly_warning": warning,
        "real_trading_enabled": False,
    }


def build_core_metric_cards(metrics: dict) -> list[dict]:
    explain = build_metric_explanations()
    return [
        _card("策略收益", metrics["strategy_return"], explain["策略收益"]),
        _card("基准收益", metrics["benchmark_return"], explain["基准收益"]),
        _card("超额收益", metrics["excess_return"], explain["超额收益"]),
        _card("年化收益", metrics["annualized_return"], explain["年化收益"]),
        _card("最大回撤", -metrics["max_drawdown"], explain["最大回撤"], "回撤越大，持有体验越难。"),
        _card("胜率", metrics["win_rate"], explain["胜率"]),
        _card("盈亏比", metrics["profit_loss_ratio"], explain["盈亏比"]),
        _card("夏普比率", metrics["sharpe"], explain["夏普比率"]),
    ]


def build_advanced_metric_cards(metrics: dict) -> list[dict]:
    explain = build_metric_explanations()
    labels = [
        ("Alpha", "alpha"),
        ("Beta", "beta"),
        ("信息比率", "information_ratio"),
        ("索提诺比率", "sortino"),
        ("波动率", "volatility"),
        ("基准波动率", "benchmark_volatility"),
        ("盈利次数", "profit_count"),
        ("亏损次数", "loss_count"),
    ]
    cards = []
    for label, key in labels:
        value = metrics[key]
        cards.append(
            {
                "label": label,
                "value": value,
                "display_value": _percent(value) if isinstance(value, float) and abs(value) < 3 else str(value),
                "direction": "positive" if isinstance(value, (int, float)) and value > 0 else "neutral",
                "explanation": explain.get(label, "高级指标用于研究人员进一步分析。"),
                "collapsed_by_default": True,
                "real_trading_enabled": False,
            }
        )
    return cards

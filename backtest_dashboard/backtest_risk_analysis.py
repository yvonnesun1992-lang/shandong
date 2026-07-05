from __future__ import annotations


def classify_backtest_risk(metrics: dict) -> str:
    drawdown = metrics.get("max_drawdown", 0)
    if drawdown <= 0.05:
        return "low"
    if drawdown <= 0.15:
        return "medium"
    return "high"


def build_risk_summary_for_user(metrics: dict) -> dict:
    level = classify_backtest_risk(metrics)
    labels = {"low": "低风险", "medium": "中等风险", "high": "高风险"}
    users = {"low": "beginner", "medium": "steady", "high": "advanced"}
    reasons = {
        "low": "风险较低，回撤相对平稳，适合先用模拟交易观察。",
        "medium": "风险中等，收益有吸引力，但需要接受阶段性回撤。",
        "high": "风险较高，普通投资者需要谨慎，建议先更换策略或降低仓位。",
    }
    return {
        "risk_level": level,
        "risk_label": labels[level],
        "risk_reason": reasons[level],
        "max_drawdown_warning": "最大回撤偏高，普通投资者需要谨慎。" if level == "high" else "最大回撤仍在可观察范围内。",
        "suitable_user": users[level],
        "paper_trading_allowed": True,
        "real_trading_enabled": False,
    }


def build_risk_analysis(metrics: dict) -> dict:
    return {
        **build_risk_summary_for_user(metrics),
        "max_drawdown": metrics.get("max_drawdown"),
        "volatility_hint": "波动越高，模拟交易时越需要控制仓位。",
        "backtest_dashboard_only": True,
        "broker_connected": False,
    }

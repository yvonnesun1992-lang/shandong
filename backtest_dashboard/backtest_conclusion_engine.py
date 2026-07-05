from __future__ import annotations


def evaluate_backtest_result(metrics: dict) -> dict:
    warnings: list[str] = []
    verdict = "promising"
    next_action = "paper_trade"
    paper_trading_recommended = True
    risk_warning = ""

    if metrics["strategy_return"] < metrics["benchmark_return"]:
        verdict = "underperformed_benchmark"
        next_action = "change_strategy"
        paper_trading_recommended = False
    if metrics["max_drawdown"] > 0.15:
        risk_warning = "最大回撤偏高，普通投资者需要谨慎。"
        next_action = "rebacktest"
        paper_trading_recommended = False
    if metrics["win_rate"] < 0.5:
        warnings.append("胜率偏低，策略稳定性一般。")

    return {
        "verdict": verdict,
        "risk_warning": risk_warning,
        "next_action": next_action,
        "paper_trading_recommended": paper_trading_recommended,
        "warnings": warnings,
        "real_trading_enabled": False,
    }


def build_backtest_conclusion(metrics: dict) -> dict:
    evaluation = evaluate_backtest_result(metrics)
    if evaluation["verdict"] == "underperformed_benchmark":
        user_summary = "这次回测没有跑赢基准，建议继续观察或更换策略。"
    elif evaluation["risk_warning"]:
        user_summary = "策略收益有亮点，但最大回撤偏高，建议重新回测或降低风险后再观察。"
    else:
        user_summary = "策略表现较好，可以考虑进入模拟交易观察。"
    return {
        **evaluation,
        "user_summary": user_summary,
        "plain_language": "先看是否跑赢基准，再看最大回撤是否能接受，最后决定是否进入模拟交易。",
        "backtest_dashboard_only": True,
    }


def build_user_friendly_verdict(metrics: dict) -> dict:
    conclusion = build_backtest_conclusion(metrics)
    return {
        "user_friendly": True,
        "headline": "策略体检结论",
        "summary": conclusion["user_summary"],
        "next_action": conclusion["next_action"],
        "paper_trading_recommended": conclusion["paper_trading_recommended"],
        "real_trading_enabled": False,
    }

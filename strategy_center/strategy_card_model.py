from __future__ import annotations

from strategy_center.strategy_backtest_preview import build_backtest_preview


def build_strategy_card(strategy: dict) -> dict:
    preview = build_backtest_preview(strategy["strategy_id"])
    return {
        "strategy_id": strategy["strategy_id"],
        "display_name": strategy["display_name"],
        "short_description": strategy["short_description"],
        "suitable_market": strategy["suitable_market"],
        "risk_level": strategy["risk_level"],
        "suitable_user": strategy["suitable_user"],
        "strategy_type": strategy["strategy_type"],
        "historical_backtest_summary": f"策略预览收益 {preview['strategy_return']:.1%}",
        "max_drawdown": preview["max_drawdown"],
        "win_rate": preview["win_rate"],
        "sharpe": preview["sharpe"],
        "current_status": "ready_for_local_backtest",
        "actions": {
            "查看详情": "enabled",
            "一键回测": "enabled",
            "加入模拟交易": "enabled for paper trading only",
            "真实交易": "disabled",
        },
        "real_trading_visible": False,
        "code_visible_by_default": False,
        "strategy_center_only": True,
    }


def build_strategy_cards(strategies: list[dict]) -> list[dict]:
    return [build_strategy_card(strategy) for strategy in strategies]

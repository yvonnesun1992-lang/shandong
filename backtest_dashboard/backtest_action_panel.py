from __future__ import annotations


def build_next_steps(strategy_id: str, conclusion: dict) -> list[str]:
    if conclusion.get("paper_trading_recommended"):
        return ["重新回测确认", "加入模拟交易观察", "导出报告留档"]
    return ["重新回测", "换一个策略", "继续观察风险"]


def build_backtest_action_panel(strategy_id: str, conclusion: dict) -> dict:
    recommended = bool(conclusion.get("paper_trading_recommended"))
    actions = [
        {"action_id": "rebacktest", "label": "重新回测", "enabled": True, "warning": "", "route": f"/backtest/{strategy_id}", "real_trading_enabled": False},
        {"action_id": "change_strategy", "label": "换一个策略", "enabled": True, "warning": "", "route": "/strategies", "real_trading_enabled": False},
        {
            "action_id": "paper_trade",
            "label": "加入模拟交易",
            "enabled": recommended,
            "warning": "" if recommended else "当前结论不建议直接加入模拟交易。",
            "route": f"/v5-live-paper?strategy={strategy_id}",
            "real_trading_enabled": False,
        },
        {"action_id": "export_report", "label": "导出报告", "enabled": True, "warning": "", "route": f"/backtest/{strategy_id}#export", "real_trading_enabled": False},
        {"action_id": "view_attribution", "label": "查看收益来源", "enabled": True, "warning": "", "route": f"/backtest/{strategy_id}#attribution", "real_trading_enabled": False},
    ]
    return {
        "strategy_id": strategy_id,
        "actions": actions,
        "next_steps": build_next_steps(strategy_id, conclusion),
        "real_trading_hidden": True,
        "order_submission_enabled": False,
        "backtest_dashboard_only": True,
    }

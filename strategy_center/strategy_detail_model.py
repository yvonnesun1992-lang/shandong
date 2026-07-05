from __future__ import annotations

from strategy_center.strategy_backtest_preview import build_backtest_preview
from strategy_center.strategy_catalog import build_strategy_catalog
from strategy_center.strategy_education_copy import explain_risk_level, explain_strategy_type, explain_suitable_market
from strategy_center.strategy_paper_trading_preview import build_paper_trading_preview


def _find_strategy(strategy_id: str) -> dict:
    for strategy in build_strategy_catalog():
        if strategy["strategy_id"] == strategy_id:
            return strategy
    return build_strategy_catalog()[0]


def build_strategy_detail_sections(strategy: dict) -> dict:
    backtest = build_backtest_preview(strategy["strategy_id"])
    paper = build_paper_trading_preview(strategy["strategy_id"])
    return {
        "策略介绍": strategy["short_description"],
        "适合谁": f"适合 {strategy['suitable_user']} 用户，{explain_suitable_market(strategy['suitable_market'])}",
        "不适合谁": "不适合想直接进行真实交易、不能接受回撤、或不愿先做模拟观察的用户。",
        "策略逻辑说明": explain_strategy_type(strategy["strategy_type"]),
        "回测表现": backtest,
        "风险指标": {
            "risk_level": strategy["risk_level"],
            "risk_explanation": explain_risk_level(strategy["risk_level"]),
            "max_drawdown": backtest["max_drawdown"],
            "sharpe": backtest["sharpe"],
        },
        "最近运行记录": ["本地预览已生成", "风险提示已确认", "模拟交易入口可用"],
        "一键操作": {
            "一键回测": "enabled",
            "加入模拟交易": "enabled for paper trading only",
            "真实交易": "hidden",
        },
        "高级代码入口": {
            "collapsed_by_default": True,
            "code_visible_by_default": False,
            "description": "高级代码入口默认折叠，普通用户无需打开。",
        },
        "模拟交易预览": paper,
    }


def build_strategy_detail(strategy_id: str) -> dict:
    strategy = _find_strategy(strategy_id)
    sections = build_strategy_detail_sections(strategy)
    return {
        "strategy": strategy,
        "sections": sections,
        "advanced_code_entry": sections["高级代码入口"],
        "paper_trading_notice": "当前为模拟环境，不会提交真实订单，不会使用真实资金。",
        "real_trading_enabled": False,
        "order_submission_enabled": False,
        "real_money_enabled": False,
        "strategy_center_only": True,
        "localhost_only": True,
        "paper_trading": True,
    }

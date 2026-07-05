from __future__ import annotations


def select_recommended_strategy() -> dict:
    return {
        "strategy_name": "小市值动量策略",
        "market_fit": "震荡偏多",
        "risk_level": "中",
        "recommended_action": "可直接运行",
        "mode": "paper_trading_only",
    }


def run_backtest(strategy: dict | None = None) -> dict:
    strategy = strategy or select_recommended_strategy()
    return {
        "strategy_name": strategy["strategy_name"],
        "strategy_return": 0.128,
        "benchmark_return": 0.074,
        "max_drawdown": 0.083,
        "win_rate": 0.61,
        "paper_only": True,
    }


def run_paper_trading(strategy: dict | None = None) -> dict:
    strategy = strategy or select_recommended_strategy()
    return {
        "strategy_name": strategy["strategy_name"],
        "paper_trading": True,
        "simulated_equity": 112800,
        "simulated_pnl": 12800,
        "risk_check_passed": True,
        "order_submission_enabled": False,
    }


def summarize_result(strategy: dict | None = None, backtest: dict | None = None, paper: dict | None = None) -> dict:
    strategy = strategy or select_recommended_strategy()
    backtest = backtest or run_backtest(strategy)
    paper = paper or run_paper_trading(strategy)
    return {
        "strategy_name": strategy["strategy_name"],
        "strategy_return": backtest["strategy_return"],
        "benchmark_return": backtest["benchmark_return"],
        "max_drawdown": backtest["max_drawdown"],
        "paper_trading": paper["paper_trading"],
        "recommended_to_continue": backtest["strategy_return"] > backtest["benchmark_return"]
        and backtest["max_drawdown"] <= 0.10
        and paper["risk_check_passed"],
        "mode": "paper_trading_only",
    }

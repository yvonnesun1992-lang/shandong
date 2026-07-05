from __future__ import annotations


DISPLAY_NAMES = {
    "small_cap_momentum": "小市值动量策略",
    "dividend_low_vol": "红利低波策略",
    "csi300_enhanced": "沪深300增强策略",
    "bank_rotation": "银行股轮动策略",
}


def build_backtest_metadata(strategy_id: str) -> dict:
    return {
        "strategy_id": strategy_id,
        "strategy_name": strategy_id,
        "display_name": DISPLAY_NAMES.get(strategy_id, "量化策略"),
        "backtest_start_date": "2023-01-03",
        "backtest_end_date": "2025-12-31",
        "initial_capital": 100000,
        "rebalance_frequency": "weekly",
        "benchmark": "沪深300",
        "run_status": "completed",
        "run_duration": "2.8s local preview",
        "trading_mode": "paper_trading",
        "real_trading_enabled": False,
    }


def build_backtest_core_metrics(strategy_id: str) -> dict:
    presets = {
        "small_cap_momentum": {
            "strategy_return": 0.186,
            "benchmark_return": 0.112,
            "annualized_return": 0.081,
            "max_drawdown": 0.118,
            "win_rate": 0.57,
            "profit_loss_ratio": 1.32,
            "sharpe": 1.18,
            "risk_level": "medium",
        },
        "dividend_low_vol": {
            "strategy_return": 0.102,
            "benchmark_return": 0.074,
            "annualized_return": 0.049,
            "max_drawdown": 0.046,
            "win_rate": 0.61,
            "profit_loss_ratio": 1.18,
            "sharpe": 1.05,
            "risk_level": "low",
        },
    }
    metrics = dict(presets.get(strategy_id, presets["small_cap_momentum"]))
    metrics["excess_return"] = metrics["strategy_return"] - metrics["benchmark_return"]
    metrics["real_trading_enabled"] = False
    return metrics


def build_backtest_advanced_metrics(strategy_id: str) -> dict:
    base = build_backtest_core_metrics(strategy_id)
    return {
        "alpha": 0.041,
        "beta": 0.83,
        "information_ratio": 0.74,
        "sortino": 1.36,
        "volatility": 0.158,
        "benchmark_volatility": 0.171,
        "max_drawdown_period": "2024-04 至 2024-06",
        "profit_count": 39,
        "loss_count": 29,
        "advanced_metrics_collapsed_by_default": True,
        "real_trading_enabled": False,
        "risk_level": base["risk_level"],
    }


def build_backtest_result(strategy_id: str) -> dict:
    return {
        "strategy_id": strategy_id,
        "metadata": build_backtest_metadata(strategy_id),
        "core_metrics": build_backtest_core_metrics(strategy_id),
        "advanced_metrics": build_backtest_advanced_metrics(strategy_id),
        "backtest_dashboard_only": True,
        "localhost_only": True,
        "paper_trading": True,
        "real_trading_enabled": False,
        "broker_connected": False,
        "sandbox_api_enabled": False,
        "order_submission_enabled": False,
        "real_money_enabled": False,
    }

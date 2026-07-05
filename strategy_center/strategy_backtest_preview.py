from __future__ import annotations


def build_backtest_preview(strategy_id: str) -> dict:
    seed = sum(ord(char) for char in strategy_id) % 7
    strategy_return = round(0.086 + seed * 0.009, 3)
    return {
        "strategy_id": strategy_id,
        "strategy_return": strategy_return,
        "benchmark_return": 0.064,
        "annualized_return": round(strategy_return * 0.82, 3),
        "max_drawdown": round(0.052 + seed * 0.006, 3),
        "win_rate": round(0.55 + seed * 0.012, 3),
        "sharpe": round(1.05 + seed * 0.08, 2),
        "backtest_status": "local_preview_ready",
        "can_run_backtest": True,
        "real_trading_enabled": False,
        "strategy_center_only": True,
    }


def summarize_backtest_preview(strategy_id: str) -> dict:
    preview = build_backtest_preview(strategy_id)
    return {
        "strategy_id": strategy_id,
        "summary": f"本地预览收益 {preview['strategy_return']:.1%}，最大回撤 {preview['max_drawdown']:.1%}。",
        **preview,
    }

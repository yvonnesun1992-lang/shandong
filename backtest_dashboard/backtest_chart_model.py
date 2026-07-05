from __future__ import annotations


DATES = ["2025-01", "2025-03", "2025-05", "2025-07", "2025-09", "2025-11"]


def build_equity_curve_chart_data(strategy_id: str) -> dict:
    strategy = [0.00, 0.032, 0.048, 0.094, 0.131, 0.186]
    benchmark = [0.00, 0.021, 0.037, 0.071, 0.086, 0.112]
    return {
        "strategy_id": strategy_id,
        "chart_type": "equity_curve",
        "points": [
            {"date": date, "strategy_return": s, "benchmark_return": b, "excess_return": s - b}
            for date, s, b in zip(DATES, strategy, benchmark, strict=True)
        ],
        "explanation": "蓝线高于基准线，代表策略跑赢市场；低于基准线，代表策略跑输市场。",
        "real_trading_enabled": False,
    }


def build_excess_return_chart_data(strategy_id: str) -> dict:
    values = [0.002, -0.004, 0.006, 0.001, -0.002, 0.008]
    return {
        "strategy_id": strategy_id,
        "chart_type": "daily_excess_return",
        "points": [
            {"date": date, "daily_excess_return": value, "direction": "outperform" if value >= 0 else "underperform"}
            for date, value in zip(DATES, values, strict=True)
        ],
        "real_trading_enabled": False,
    }


def build_daily_trade_action_chart_data(strategy_id: str) -> dict:
    buys = [12000, 0, 8000, 5000, 0, 7000]
    sells = [0, 4000, 0, 2500, 6000, 0]
    return {
        "strategy_id": strategy_id,
        "chart_type": "daily_trade_action",
        "points": [
            {"date": date, "buy_amount": buy, "sell_amount": sell, "net_amount": buy - sell}
            for date, buy, sell in zip(DATES, buys, sells, strict=True)
        ],
        "order_submission_enabled": False,
        "real_trading_enabled": False,
    }


def build_drawdown_chart_data(strategy_id: str) -> dict:
    drawdowns = [0.0, -0.018, -0.041, -0.026, -0.073, -0.031]
    return {
        "strategy_id": strategy_id,
        "chart_type": "drawdown",
        "points": [{"date": date, "drawdown": value} for date, value in zip(DATES, drawdowns, strict=True)],
        "real_trading_enabled": False,
    }


def build_backtest_charts(strategy_id: str) -> dict:
    return {
        "equity_curve": build_equity_curve_chart_data(strategy_id),
        "daily_excess_return": build_excess_return_chart_data(strategy_id),
        "daily_trade_action": build_daily_trade_action_chart_data(strategy_id),
        "drawdown": build_drawdown_chart_data(strategy_id),
        "backtest_dashboard_only": True,
        "paper_trading": True,
    }

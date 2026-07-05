from __future__ import annotations


def build_paper_trading_preview(strategy_id: str) -> dict:
    return {
        "strategy_id": strategy_id,
        "paper_trading_available": True,
        "simulated_capital_placeholder": "100,000 local paper capital",
        "latest_signal_placeholder": "HOLD / wait for next local signal",
        "risk_status_placeholder": "risk check passed",
        "order_submission_enabled": False,
        "real_money_enabled": False,
        "strategy_center_only": True,
        "paper_trading": True,
    }


def summarize_paper_trading_preview(strategy_id: str) -> dict:
    preview = build_paper_trading_preview(strategy_id)
    return {
        "strategy_id": strategy_id,
        "summary": "可加入本地模拟交易观察，不会提交真实订单。",
        **preview,
    }

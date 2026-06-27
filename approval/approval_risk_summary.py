from __future__ import annotations

from typing import Any


def build_approval_risk_summary(order_intent: dict[str, Any], paper_state: dict[str, Any] | None = None) -> dict[str, Any]:
    quantity = float(order_intent.get("quantity", 0) or 0)
    price = float(order_intent.get("price", order_intent.get("market_price", 0)) or 0)
    strength = float(order_intent.get("strength", order_intent.get("signal_strength", 0)) or 0)
    return {
        "symbol": str(order_intent.get("symbol", "")).upper(),
        "side": str(order_intent.get("side", order_intent.get("action", ""))).upper(),
        "quantity": quantity,
        "estimated_notional": round(quantity * price, 6),
        "signal_strength": max(0.0, min(1.0, strength)),
        "position_limit_check": "planned",
        "drawdown_check": "planned",
        "daily_loss_check": "planned",
        "paper_state": _safe_paper_state(paper_state or {}),
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
    }


def _safe_paper_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "cash": state.get("cash"),
        "equity": state.get("equity"),
        "positions_count": len(state.get("positions", {}) or {}),
    }

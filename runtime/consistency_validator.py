from __future__ import annotations

import math


class ConsistencyValidator:
    def validate(self, final_state: dict, checkpoint_state: dict | None = None) -> dict:
        checks = []
        errors = []
        cash = float(final_state.get("cash", 0.0))
        position_value = float(final_state.get("position_value", 0.0))
        equity = float(final_state.get("equity", 0.0))
        positions = final_state.get("positions", {}) or {}
        if cash < -1e-6:
            errors.append("cash is negative")
        checks.append("cash_non_negative")
        for symbol, position in positions.items():
            if float(position.get("quantity", 0.0)) < -1e-6:
                errors.append(f"negative position: {symbol}")
        checks.append("positions_non_negative")
        if abs((cash + position_value) - equity) > 1e-4:
            errors.append("equity does not equal cash plus position value")
        checks.append("equity_identity")
        for field in ("realized_pnl", "unrealized_pnl"):
            value = float(final_state.get(field, 0.0))
            if math.isnan(value):
                errors.append(f"{field} is NaN")
        checks.append("pnl_not_nan")
        if checkpoint_state:
            checkpoint_portfolio = checkpoint_state.get("portfolio", {})
            if checkpoint_portfolio and "cash" not in checkpoint_portfolio:
                errors.append("checkpoint missing cash")
            checks.append("checkpoint_basic_state")
        for order in final_state.get("active_orders", []) or []:
            if order.get("status", "NEW") not in {"NEW", "FILLED", "REJECTED", "CANCELLED"}:
                errors.append("illegal open order status")
        checks.append("open_order_status")
        return {"consistent": not errors, "checks": checks, "errors": errors}



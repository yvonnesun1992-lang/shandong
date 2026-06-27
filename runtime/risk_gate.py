from __future__ import annotations

from runtime.event_bus import EventBus
from trading.risk_limits import RiskLimits


class RiskGate:
    def __init__(self, limits: RiskLimits | None = None, event_bus: EventBus | None = None) -> None:
        self.limits = limits or RiskLimits()
        self.event_bus = event_bus or EventBus()
        self.kill_switch_active = False

    def pre_trade_check(self, order, account, market_price: float) -> dict:
        if self.kill_switch_active:
            result = {"approved": False, "reason": "KILL_SWITCH_ACTIVE"}
            self.event_bus.publish("RISK_TRIGGERED", result)
            return result
        result = self.limits.validate_order(order, account, market_price)
        if not result["approved"]:
            self.event_bus.publish("RISK_TRIGGERED", result)
        return result

    def post_trade_validation(self, account_summary: dict) -> dict:
        risk = self.limits.update_equity(float(account_summary.get("equity", 0.0)))
        if risk["stop_new_positions"]:
            self.trigger_kill_switch("DRAWDOWN_OR_DAILY_LOSS")
        return risk

    def trigger_kill_switch(self, reason: str) -> None:
        self.kill_switch_active = True
        self.event_bus.publish("RISK_TRIGGERED", {"reason": reason, "kill_switch_active": True})



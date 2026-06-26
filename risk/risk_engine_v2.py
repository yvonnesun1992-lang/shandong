from __future__ import annotations

import pandas as pd


class RiskEngineV2:
    def __init__(
        self,
        max_position_exposure: float = 0.10,
        max_daily_loss: float = 0.03,
        max_drawdown: float = 0.10,
        volatility_spike_threshold: float = 0.05,
    ) -> None:
        self.max_position_exposure = float(max_position_exposure)
        self.max_daily_loss = float(max_daily_loss)
        self.max_drawdown = float(max_drawdown)
        self.volatility_spike_threshold = float(volatility_spike_threshold)
        self.kill_switch_active = False
        self._peak_equity = 0.0
        self._day_start_equity: dict[str, float] = {}
        self.last_reason = "OK"

    def update_equity(self, equity: float, timestamp) -> dict:
        current = float(equity)
        ts = pd.Timestamp(timestamp)
        day = str(ts.date())
        self._peak_equity = max(self._peak_equity, current)
        self._day_start_equity.setdefault(day, current)
        drawdown = (self._peak_equity - current) / self._peak_equity if self._peak_equity > 0 else 0.0
        daily_loss = (self._day_start_equity[day] - current) / self._day_start_equity[day] if self._day_start_equity[day] > 0 else 0.0
        if drawdown > self.max_drawdown or daily_loss > self.max_daily_loss:
            self.stop_all_trading("DRAWDOWN_LIMIT" if drawdown > self.max_drawdown else "DAILY_LOSS_LIMIT")
        return {"drawdown": float(drawdown), "daily_loss": float(daily_loss), "kill_switch_active": self.kill_switch_active}

    def stop_all_trading(self, reason: str = "KILL_SWITCH") -> None:
        self.kill_switch_active = True
        self.last_reason = reason

    def validate_order(self, order: dict, portfolio_snapshot: dict, volatility: float = 0.0, regime: str = "sideways") -> dict:
        if self.kill_switch_active:
            return {"approved": False, "reason": "KILL_SWITCH_ACTIVE", "scale": 0.0}
        if float(volatility) > self.volatility_spike_threshold:
            return {"approved": False, "reason": "VOLATILITY_SPIKE", "scale": 0.0}
        equity = float(portfolio_snapshot.get("equity", 0.0) or 0.0)
        notional = float(order.get("quantity", 0.0)) * float(order.get("price", 0.0))
        if equity > 0 and notional / equity > self.max_position_exposure:
            return {"approved": False, "reason": "MAX_POSITION_EXPOSURE", "scale": self.max_position_exposure}
        return {"approved": True, "reason": "OK", "scale": self.dynamic_risk_scale(float(volatility), regime)}

    def dynamic_risk_scale(self, volatility: float, regime: str) -> float:
        scale = 1.0
        if volatility > self.volatility_spike_threshold / 2:
            scale *= 0.5
        if regime == "bear":
            scale *= 0.5
        return float(max(0.0, min(1.0, scale)))

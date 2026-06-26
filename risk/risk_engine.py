from __future__ import annotations

import numpy as np
import pandas as pd


class RiskEngine:
    def __init__(
        self,
        max_position_per_asset: float = 0.10,
        max_drawdown: float = 0.10,
        high_volatility_threshold: float = 0.35,
    ) -> None:
        self.max_position_per_asset = max_position_per_asset
        self.max_drawdown = max_drawdown
        self.high_volatility_threshold = high_volatility_threshold

    def evaluate_order(
        self,
        symbol: str,
        action: str,
        desired_value: float,
        portfolio_value: float,
        current_positions: dict[str, float] | None = None,
        equity_curve=None,
        volatility: float = 0.0,
    ) -> dict:
        current_positions = current_positions or {}
        desired_value = max(float(desired_value or 0.0), 0.0)
        portfolio_value = max(float(portfolio_value or 0.0), 0.0)
        current_value = max(float(current_positions.get(symbol, 0.0) or 0.0), 0.0)
        reasons: list[str] = []
        exposure_multiplier = 1.0

        approved_value = desired_value
        if action == "BUY" and portfolio_value > 0:
            max_allowed = max(portfolio_value * self.max_position_per_asset - current_value, 0.0)
            if approved_value > max_allowed:
                approved_value = max_allowed
                reasons.append("max_position_per_asset")

        drawdown = self._current_drawdown(equity_curve)
        if drawdown > self.max_drawdown:
            exposure_multiplier *= 0.5
            reasons.append("drawdown_control")

        volatility = max(float(volatility or 0.0), 0.0)
        if volatility > self.high_volatility_threshold:
            exposure_multiplier *= 0.5
            reasons.append("volatility_deleveraging")

        approved_value *= exposure_multiplier
        concentration = current_value / portfolio_value if portfolio_value > 0 else 0.0
        risk_score = min(
            100.0,
            drawdown / max(self.max_drawdown, 1e-12) * 35
            + volatility / max(self.high_volatility_threshold, 1e-12) * 35
            + concentration / max(self.max_position_per_asset, 1e-12) * 30,
        )

        return {
            "symbol": symbol,
            "action": action,
            "approved_value": float(max(approved_value, 0.0)),
            "exposure_multiplier": float(exposure_multiplier),
            "risk_score": float(risk_score),
            "drawdown": float(drawdown),
            "volatility": float(volatility),
            "reasons": reasons,
        }

    @staticmethod
    def _current_drawdown(equity_curve) -> float:
        if equity_curve is None:
            return 0.0
        series = pd.Series(equity_curve, dtype="float64").replace([np.inf, -np.inf], np.nan).dropna()
        if series.empty:
            return 0.0
        peak = series.cummax()
        drawdown = ((peak - series) / peak.replace(0, np.nan)).fillna(0.0)
        return float(drawdown.iloc[-1])

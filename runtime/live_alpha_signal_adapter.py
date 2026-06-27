from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from feature_engine.factors import calculate_factors
from quant_core_v5.alpha_engine.alpha_model import AlphaModel


DEFAULT_LIVE_FACTORS = ["momentum_20d", "trend_strength", "breakout_strength"]


class LiveAlphaSignalAdapter:
    def __init__(self, min_window: int = 60, factors: list[str] | None = None) -> None:
        self.min_window = int(min_window)
        self.factors = factors or DEFAULT_LIVE_FACTORS
        self.alpha_model = AlphaModel()

    def generate_signal(self, symbol: str, frame: pd.DataFrame) -> dict:
        symbol = str(symbol).upper()
        timestamp = _timestamp(frame)
        if frame is None or frame.empty or len(frame) < self.min_window:
            return _signal(symbol, "HOLD", 0.0, timestamp, warning="insufficient feature window")
        try:
            factors = calculate_factors(frame)
            factor_matrices = {}
            for factor in self.factors:
                if factor in factors.columns:
                    factor_matrices[factor] = pd.DataFrame({symbol: factors.set_index("datetime")[factor]})
            if not factor_matrices:
                return _signal(symbol, "HOLD", 0.0, timestamp, warning="no live alpha factors")
            factor_weight = 1.0 / len(factor_matrices)
            alpha_scores = self.alpha_model.build_alpha_scores(factor_matrices, {factor: factor_weight for factor in factor_matrices})
            if alpha_scores.empty or symbol not in alpha_scores.columns:
                return _signal(symbol, "HOLD", 0.0, timestamp, warning="empty alpha score")
            latest_score = alpha_scores[symbol].dropna().tail(1)
            if latest_score.empty:
                return _signal(symbol, "HOLD", 0.0, timestamp, warning="missing latest alpha score")
            score = float(latest_score.iloc[0])
            strength = max(0.0, min(1.0, abs(score)))
            if score > 0.05:
                return _signal(symbol, "BUY", strength, timestamp)
            if score < -0.05:
                return _signal(symbol, "SELL", strength, timestamp)
            return _signal(symbol, "HOLD", strength, timestamp)
        except Exception as exc:
            return _signal(symbol, "HOLD", 0.0, timestamp, warning=f"alpha adapter fallback: {type(exc).__name__}")

    def generate_signals(self, frames: dict[str, pd.DataFrame]) -> list[dict]:
        return [self.generate_signal(symbol, frame) for symbol, frame in sorted((frames or {}).items())]


def _signal(symbol: str, action: str, strength: float, timestamp: str, warning: str = "") -> dict:
    signal = {
        "symbol": symbol,
        "action": action,
        "strength": float(max(0.0, min(1.0, strength))),
        "timestamp": timestamp,
        "source": "v5_alpha",
        "paper_trading": True,
        "real_trading": False,
    }
    if warning:
        signal["warning"] = warning
    return signal


def _timestamp(frame: pd.DataFrame | None) -> str:
    if frame is not None and not frame.empty and "datetime" in frame:
        value = pd.to_datetime(frame["datetime"]).max()
        return value.isoformat()
    return datetime.now(UTC).replace(microsecond=0).isoformat()

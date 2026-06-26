from __future__ import annotations

import pandas as pd

from strategies.ma_crossover import MACrossoverStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy


class VolatilityBreakoutStrategy:
    def __init__(self, window: int = 20, breakout_multiplier: float = 1.5) -> None:
        self.window = window
        self.breakout_multiplier = breakout_multiplier

    def generate_signal(self, data: pd.DataFrame, symbol: str) -> dict:
        frame = _prepare(data)
        if len(frame) < self.window:
            return _signal(symbol, "HOLD", 0.0, frame)

        recent = frame.tail(self.window)
        high = recent["high"].iloc[:-1].max()
        low = recent["low"].iloc[:-1].min()
        close = recent["close"].iloc[-1]
        returns = recent["close"].pct_change().fillna(0)
        volatility = float(returns.std(ddof=0))
        buffer = abs(close) * volatility * self.breakout_multiplier

        if close > high + buffer:
            strength = min((close - high) / max(buffer, 1e-12), 1.0)
            return _signal(symbol, "BUY", strength, frame)
        if close < low - buffer:
            strength = min((low - close) / max(buffer, 1e-12), 1.0)
            return _signal(symbol, "SELL", strength, frame)
        return _signal(symbol, "HOLD", 0.0, frame)


class StrategyEnsemble:
    def __init__(self, vote_threshold: float = 0.2, strategies: dict | None = None) -> None:
        self.vote_threshold = vote_threshold
        self.strategies = strategies or {
            "ma": MACrossoverStrategy(),
            "momentum": MomentumStrategy(threshold=0.03),
            "mean_reversion": MeanReversionStrategy(),
            "volatility_breakout": VolatilityBreakoutStrategy(),
        }

    def generate_signal(self, data: pd.DataFrame, symbol: str, regime: dict | None = None) -> dict:
        frame = _prepare(data)
        weights = self._weights_for_regime(regime or {"state": "sideways", "confidence": 0.0})
        strategy_signals = {}
        vote_score = 0.0

        for name, strategy in self.strategies.items():
            signal = strategy.generate_signal(frame, symbol)
            strategy_signals[name] = signal
            direction = 1 if signal["action"] == "BUY" else -1 if signal["action"] == "SELL" else 0
            vote_score += weights.get(name, 0.0) * direction * float(signal.get("strength", 0.0))

        if vote_score > self.vote_threshold:
            action = "BUY"
        elif vote_score < -self.vote_threshold:
            action = "SELL"
        else:
            action = "HOLD"

        timestamp = frame["datetime"].iloc[-1] if not frame.empty else pd.Timestamp.utcnow()
        return {
            "symbol": symbol,
            "action": action,
            "strength": float(min(abs(vote_score), 1.0)),
            "timestamp": timestamp,
            "vote_score": float(max(-1.0, min(vote_score, 1.0))),
            "weights": weights,
            "strategy_signals": strategy_signals,
        }

    @staticmethod
    def _weights_for_regime(regime: dict) -> dict[str, float]:
        state = str(regime.get("state", "sideways")).lower()
        if state == "bull":
            weights = {"ma": 0.25, "momentum": 0.40, "mean_reversion": 0.15, "volatility_breakout": 0.20}
        elif state == "bear":
            weights = {"ma": 0.20, "momentum": 0.20, "mean_reversion": 0.40, "volatility_breakout": 0.20}
        else:
            weights = {"ma": 0.25, "momentum": 0.25, "mean_reversion": 0.25, "volatility_breakout": 0.25}
        total = sum(weights.values()) or 1.0
        return {key: value / total for key, value in weights.items()}


def _prepare(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").ffill().bfill().fillna(0)
    return frame.sort_values("datetime").reset_index(drop=True)


def _signal(symbol: str, action: str, strength: float, frame: pd.DataFrame) -> dict:
    timestamp = frame["datetime"].iloc[-1] if not frame.empty else pd.Timestamp.utcnow()
    return {"symbol": symbol, "action": action, "strength": float(max(0.0, min(strength, 1.0))), "timestamp": timestamp}

from __future__ import annotations

import pandas as pd

from live.data_stream import MarketEvent, StreamingBuffer
from quant_core_v5.pipeline import run_alpha_pipeline_from_market_data


class LiveSignalEngine:
    def __init__(self, min_history: int = 80, buffer_size: int = 390, max_weight_per_asset: float = 0.40) -> None:
        self.min_history = int(min_history)
        self.buffer = StreamingBuffer(maxlen=buffer_size)
        self.max_weight_per_asset = float(max_weight_per_asset)
        self.last_signal_timestamp: pd.Timestamp | None = None
        self.last_history_end: pd.Timestamp | None = None
        self.regime_state = {"state": "sideways", "confidence": 0.0}

    def on_market_event(self, event: MarketEvent) -> list[dict]:
        self.buffer.append(event)
        market_data = self.buffer.to_market_data()
        if not market_data or min(len(frame) for frame in market_data.values()) < self.min_history:
            return []
        self.last_history_end = max(pd.Timestamp(frame["datetime"].max()) for frame in market_data.values())
        self.regime_state = _detect_live_regime(market_data)
        result = run_alpha_pipeline_from_market_data(
            market_data=market_data,
            regime=self.regime_state,
            max_weight_per_asset=max(self.max_weight_per_asset, 1.0 / max(len(market_data), 1)),
            transaction_cost_bps=10.0,
            slippage_bps=5.0,
        )
        alpha_scores = result["alpha"]["alpha_scores"]
        if alpha_scores.empty:
            return []
        latest = alpha_scores.iloc[-1].sort_values(ascending=False)
        signals = []
        for symbol, score in latest.items():
            value = float(score) if pd.notna(score) else 0.0
            if value > 0.25:
                action = "BUY"
            elif value < -0.25:
                action = "SELL"
            else:
                action = "HOLD"
            signals.append(
                {
                    "symbol": str(symbol),
                    "action": action,
                    "strength": abs(value),
                    "timestamp": pd.Timestamp(event.timestamp),
                    "regime": self.regime_state["state"],
                }
            )
        self.last_signal_timestamp = pd.Timestamp(event.timestamp)
        return signals


def _detect_live_regime(market_data: dict[str, pd.DataFrame]) -> dict:
    closes = []
    for frame in market_data.values():
        close = pd.to_numeric(frame["close"], errors="coerce").dropna()
        if len(close) >= 20:
            closes.append(close.pct_change().dropna())
    if not closes:
        return {"state": "sideways", "confidence": 0.0}
    market_returns = pd.concat(closes, axis=1).mean(axis=1).dropna()
    momentum = float(market_returns.tail(20).sum()) if len(market_returns) else 0.0
    volatility = float(market_returns.tail(20).std(ddof=0)) if len(market_returns) else 0.0
    if momentum > 0.01 and volatility < 0.03:
        return {"state": "bull", "confidence": min(1.0, abs(momentum) * 20)}
    if momentum < -0.01 or volatility > 0.05:
        return {"state": "bear", "confidence": min(1.0, abs(momentum) * 20 + volatility * 5)}
    return {"state": "sideways", "confidence": 0.5}

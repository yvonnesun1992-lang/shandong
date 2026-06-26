from __future__ import annotations


class PortfolioOptimizer:
    def __init__(self, max_weight: float = 0.40, risk_penalty: float = 1.0) -> None:
        self.max_weight = max_weight
        self.risk_penalty = risk_penalty

    def allocate(self, signals: list[dict], volatility: dict[str, float] | None = None, regime: dict | None = None) -> dict[str, float]:
        volatility = volatility or {}
        regime = regime or {"state": "sideways", "confidence": 0.0}
        state = str(regime.get("state", "sideways")).lower()
        confidence = max(0.0, min(float(regime.get("confidence", 0.0) or 0.0), 1.0))
        regime_multiplier = 1.0 + (0.15 * confidence if state == "bull" else -0.10 * confidence if state == "bear" else 0.0)

        raw_scores: dict[str, float] = {}
        for signal in signals:
            if signal.get("action") != "BUY":
                continue
            symbol = str(signal.get("symbol", "")).strip().upper()
            if not symbol:
                continue
            strength = max(float(signal.get("strength", 0.0) or 0.0), 0.0)
            vol = max(float(volatility.get(symbol, 0.20) or 0.20), 1e-6)
            raw_scores[symbol] = strength * regime_multiplier / (1.0 + self.risk_penalty * vol)

        if not raw_scores:
            return {}

        total = sum(raw_scores.values()) or 1.0
        weights = {symbol: score / total for symbol, score in raw_scores.items()}
        return _cap_and_redistribute(weights, self.max_weight)


def _cap_and_redistribute(weights: dict[str, float], max_weight: float) -> dict[str, float]:
    if not weights:
        return {}
    max_weight = max(float(max_weight), 0.0)
    if max_weight * len(weights) < 1.0:
        max_weight = 1.0 / len(weights)

    remaining = dict(weights)
    capped: dict[str, float] = {}
    while remaining:
        total = sum(remaining.values()) or 1.0
        provisional = {symbol: value / total * (1.0 - sum(capped.values())) for symbol, value in remaining.items()}
        over = {symbol: value for symbol, value in provisional.items() if value > max_weight}
        if not over:
            capped.update(provisional)
            break
        for symbol in over:
            capped[symbol] = max_weight
            remaining.pop(symbol, None)
    total = sum(capped.values()) or 1.0
    return {symbol: value / total for symbol, value in capped.items()}

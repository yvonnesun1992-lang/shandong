from __future__ import annotations


class RegimeAdjuster:
    def adjust(self, weights: dict[str, float], regime: dict) -> dict[str, float]:
        if not weights:
            return {}
        state = str(regime.get("state", "sideways")).lower()
        confidence = max(0.0, min(float(regime.get("confidence", 0.0) or 0.0), 1.0))
        adjusted = dict(weights)

        if state == "bull":
            self._tilt(adjusted, "momentum", 1.0 + 0.5 * confidence)
        elif state == "bear":
            self._tilt(adjusted, "mean_reversion", 1.0 + 0.5 * confidence)
        else:
            average = 1.0 / len(adjusted)
            adjusted = {key: average * 0.7 + value * 0.3 for key, value in adjusted.items()}

        total = sum(adjusted.values()) or 1.0
        return {key: value / total for key, value in adjusted.items()}

    @staticmethod
    def _tilt(weights: dict[str, float], keyword: str, multiplier: float) -> None:
        for key in list(weights):
            if keyword in key:
                weights[key] *= multiplier

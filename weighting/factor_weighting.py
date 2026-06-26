from __future__ import annotations

import math


def compute_factor_weights(ic_results: list[dict]) -> dict[str, float]:
    raw_scores = {}
    for result in ic_results:
        factor = str(result.get("factor", "unknown"))
        ic_mean = float(result.get("ic_mean", 0.0) or 0.0)
        ic_ir = float(result.get("ic_ir", 0.0) or 0.0)
        stability = float(result.get("ic_stability", 0.0) or 0.0)
        recent_decay = _recent_decay(result.get("rolling_ic_20"))
        raw_scores[factor] = max(ic_mean, 0.0) * max(ic_ir, 0.0) * max(stability, 0.0) * recent_decay

    if not raw_scores:
        return {}
    return _softmax(raw_scores)


def _recent_decay(rolling_ic) -> float:
    if rolling_ic is None:
        return 1.0
    series = getattr(rolling_ic, "dropna", lambda: [])()
    if len(series) < 2:
        return 1.0
    older = float(series.iloc[0])
    recent = float(series.iloc[-1])
    return max(0.5, 1.0 + (recent - older))


def _softmax(scores: dict[str, float]) -> dict[str, float]:
    values = list(scores.values())
    peak = max(values)
    exps = {key: math.exp(value - peak) for key, value in scores.items()}
    total = sum(exps.values()) or 1.0
    return {key: value / total for key, value in exps.items()}

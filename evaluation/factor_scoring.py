from __future__ import annotations

import pandas as pd


def score_factors(ic_results: list[dict]) -> pd.DataFrame:
    rows = []
    for result in ic_results:
        ic_mean = float(result.get("ic_mean", 0.0) or 0.0)
        ic_ir = float(result.get("ic_ir", 0.0) or 0.0)
        stability = float(result.get("ic_stability", result.get("stability", 0.0)) or 0.0)
        turnover_penalty = float(result.get("turnover_penalty", 0.0) or 0.0)
        score = ic_mean * ic_ir * stability - turnover_penalty
        rows.append(
            {
                "factor": result.get("factor", "unknown"),
                "ic_mean": ic_mean,
                "ic_std": float(result.get("ic_std", 0.0) or 0.0),
                "ic_ir": ic_ir,
                "ic_stability": stability,
                "turnover_penalty": turnover_penalty,
                "score": float(score),
            }
        )
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)

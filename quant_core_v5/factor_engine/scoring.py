from __future__ import annotations

import pandas as pd

from evaluation.ic_analysis import calculate_factor_ic
from weighting.factor_weighting import compute_factor_weights


def score_factor_set(factor_matrices: dict[str, pd.DataFrame], price_matrix: pd.DataFrame, forward_days: int = 1) -> dict:
    ic_results = [
        calculate_factor_ic(factor=factor, factor_matrix=matrix, price_matrix=price_matrix, forward_days=forward_days)
        for factor, matrix in factor_matrices.items()
    ]
    factor_weights = compute_factor_weights(ic_results)
    return {"ic_results": ic_results, "factor_weights": factor_weights}

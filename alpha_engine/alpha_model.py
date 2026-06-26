from __future__ import annotations

import pandas as pd

from alpha_engine.normalization import normalize_factor_matrix


class AlphaModel:
    def build_alpha_scores(self, factor_matrices: dict[str, pd.DataFrame], factor_weights: dict[str, float]) -> pd.DataFrame:
        normalized = {}
        for factor, matrix in factor_matrices.items():
            normalized[factor] = normalize_factor_matrix(matrix)

        combined = None
        for factor, weight in factor_weights.items():
            if factor not in normalized:
                continue
            weighted = normalized[factor] * float(weight)
            combined = weighted if combined is None else combined.add(weighted, fill_value=0.0)
        if combined is None:
            return pd.DataFrame()
        return combined.sort_index()

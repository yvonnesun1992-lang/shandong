from __future__ import annotations

import pandas as pd

from feature_engine.factors import calculate_factors


class FactorBuilder:
    def build_factor_matrix(self, universe: dict[str, pd.DataFrame], factor_name: str) -> pd.DataFrame:
        series_by_symbol = {}
        for symbol, data in universe.items():
            factors = calculate_factors(data)
            if factor_name not in factors.columns:
                raise ValueError(f"Unknown factor: {factor_name}")
            series = factors.set_index("datetime")[factor_name].astype(float)
            series_by_symbol[str(symbol).upper()] = series
        return _clean_matrix(pd.DataFrame(series_by_symbol))

    def build_price_matrix(self, universe: dict[str, pd.DataFrame], price_column: str = "close") -> pd.DataFrame:
        series_by_symbol = {}
        for symbol, data in universe.items():
            frame = data.copy()
            frame["datetime"] = pd.to_datetime(frame["datetime"])
            frame[price_column] = pd.to_numeric(frame[price_column], errors="coerce")
            series_by_symbol[str(symbol).upper()] = frame.sort_values("datetime").set_index("datetime")[price_column]
        return _clean_matrix(pd.DataFrame(series_by_symbol))


def _clean_matrix(matrix: pd.DataFrame) -> pd.DataFrame:
    matrix.index = pd.to_datetime(matrix.index)
    return matrix.sort_index().replace([float("inf"), float("-inf")], pd.NA).ffill().bfill().fillna(0)

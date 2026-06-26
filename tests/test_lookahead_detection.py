from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


TARGET_FILES = [
    Path("feature_engine/factors.py"),
    Path("factor_engine/factor_builder.py"),
    Path("portfolio/factor_portfolio.py"),
    Path("alpha_engine/normalization.py"),
    Path("portfolio/multi_factor_portfolio.py"),
]


def test_no_bfill_in_factor_research_runtime_files():
    for path in TARGET_FILES:
        text = path.read_text(encoding="utf-8")
        assert ".bfill(" not in text
        assert "bfill()" not in text
        assert "fillna(method=\"bfill\")" not in text


def test_factor_generation_does_not_backfill_warmup_values():
    from feature_engine.factors import calculate_factors

    dates = pd.date_range("2024-01-01", periods=30)
    close = pd.Series(np.arange(30, dtype=float) + 100)
    frame = pd.DataFrame(
        {
            "datetime": dates,
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": 1000,
        }
    )

    factors = calculate_factors(frame)

    assert pd.isna(factors.loc[0, "momentum_20d"])
    assert pd.isna(factors.loc[19, "momentum_20d"])
    assert not pd.isna(factors.loc[20, "momentum_20d"])


def test_factor_builder_does_not_backfill_missing_asset_history():
    from factor_engine.factor_builder import FactorBuilder

    dates = pd.date_range("2024-01-01", periods=40)
    full = _asset_frame(dates, 100)
    late = _asset_frame(dates[10:], 200)
    matrix = FactorBuilder().build_price_matrix({"FULL": full, "LATE": late})

    assert pd.isna(matrix.loc[dates[0], "LATE"])
    assert pd.isna(matrix.loc[dates[9], "LATE"])
    assert matrix.loc[dates[10], "LATE"] == 200


def test_ic_uses_factor_t_against_t_plus_one_return():
    from evaluation.ic_analysis import calculate_factor_ic

    dates = pd.date_range("2024-01-01", periods=5)
    factor_matrix = pd.DataFrame(
        {
            "A": [5, 5, 5, 5, 5],
            "B": [1, 1, 1, 1, 1],
            "C": [3, 3, 3, 3, 3],
        },
        index=dates,
    )
    # Day 0 next-day returns are perfectly positively ordered with day 0 factors.
    price_matrix = pd.DataFrame(
        {
            "A": [100, 110, 110, 110, 110],
            "B": [100, 90, 90, 90, 90],
            "C": [100, 100, 100, 100, 100],
        },
        index=dates,
    )

    result = calculate_factor_ic("demo", factor_matrix, price_matrix, forward_days=1)

    assert result["ic_series"].index[0] == dates[0]
    assert result["ic_series"].index[-1] == dates[-2]
    assert result["ic_series"].iloc[0] > 0.99


def test_factor_portfolio_uses_prior_signal_for_next_period_return():
    from portfolio.factor_portfolio import FactorPortfolioSimulator

    dates = pd.date_range("2024-01-01", periods=4)
    factor_matrix = pd.DataFrame(
        {
            "A": [10.0, 1.0, 1.0, 1.0],
            "B": [0.0, 9.0, 9.0, 9.0],
        },
        index=dates,
    )
    price_matrix = pd.DataFrame(
        {
            "A": [100.0, 110.0, 110.0, 110.0],
            "B": [100.0, 90.0, 100.0, 100.0],
        },
        index=dates,
    )

    result = FactorPortfolioSimulator().simulate(
        factor_matrices={"demo": factor_matrix},
        price_matrix=price_matrix,
        factor_scores={"demo": 1.0},
        forward_days=1,
    )

    assert result["portfolio_returns"].index[0] == dates[1]
    assert result["portfolio_returns"].iloc[0] > 0.09


def test_train_test_and_walk_forward_split_are_chronological():
    from evaluation.splits import train_test_split_time, walk_forward_splits

    index = pd.date_range("2024-01-01", periods=20)
    train, test = train_test_split_time(index, train_ratio=0.6)
    assert train.max() < test.min()
    assert len(train) == 12

    splits = list(walk_forward_splits(index, train_size=8, test_size=4, step_size=4))
    assert len(splits) == 3
    for split in splits:
        assert split["train_index"].max() < split["test_index"].min()


def _asset_frame(dates: pd.DatetimeIndex, start: float) -> pd.DataFrame:
    close = pd.Series(np.arange(len(dates), dtype=float) + start)
    return pd.DataFrame(
        {
            "datetime": dates,
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": 1000,
        }
    )

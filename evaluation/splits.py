from __future__ import annotations

import pandas as pd


def train_test_split_time(index, train_ratio: float = 0.7) -> tuple[pd.DatetimeIndex, pd.DatetimeIndex]:
    ordered = pd.DatetimeIndex(pd.to_datetime(index)).sort_values().unique()
    if len(ordered) < 2:
        return ordered, pd.DatetimeIndex([])
    split_at = int(len(ordered) * train_ratio)
    split_at = min(max(split_at, 1), len(ordered) - 1)
    return ordered[:split_at], ordered[split_at:]


def walk_forward_splits(index, train_size: int, test_size: int, step_size: int | None = None):
    ordered = pd.DatetimeIndex(pd.to_datetime(index)).sort_values().unique()
    if train_size <= 0 or test_size <= 0:
        raise ValueError("train_size and test_size must be positive")
    step = step_size or test_size
    if step <= 0:
        raise ValueError("step_size must be positive")
    start = 0
    while start + train_size + test_size <= len(ordered):
        train_index = ordered[start : start + train_size]
        test_index = ordered[start + train_size : start + train_size + test_size]
        yield {"train_index": train_index, "test_index": test_index}
        start += step

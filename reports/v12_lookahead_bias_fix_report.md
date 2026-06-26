# V1.2 Look-Ahead Bias Fix Report

## Verdict

V1.2 has been repaired from a future-leakage-prone factor research prototype into a stricter causal time-series research system.

## Fixes Applied

- Removed future backfill from factor generation.
- Removed future backfill from factor and price matrix construction.
- Removed future backfill from factor portfolio simulation.
- Preserved warm-up NaN values until enough historical data exists.
- Added chronological train/test and walk-forward split helpers.
- Updated factor portfolio simulation so prior factor signals drive next-period returns.
- Added look-ahead detection tests that fail if runtime factor research files reintroduce backfill.

## Time Alignment

The repaired research path now follows:

1. Factor values are computed using information available at time `t`.
2. IC analysis compares `factor(t)` with `return(t -> t+1)` or `return(t -> t+N)`.
3. Portfolio simulation shifts factor scores forward so signal information from `t` is applied to the next return period.
4. Missing early asset histories remain missing instead of being filled from future observations.

## Train/Test Split

The new `evaluation/splits.py` module provides:

- `train_test_split_time`
- `walk_forward_splits`

These helpers make it possible to score/select factors on a training period and evaluate them on later test windows.

## Remaining Research Caveats

- IC and factor ranking still need real-market validation before claiming alpha.
- Transaction costs, borrow limits, liquidity, survivorship bias, and universe membership changes are not fully modeled.
- The sample factor report remains a deterministic smoke-test example, not investment evidence.

## Safety Boundary

- No broker API
- No real trading
- No auto order routing
- No external AI API
- No real-money execution

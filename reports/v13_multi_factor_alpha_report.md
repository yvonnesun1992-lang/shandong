# V1.3 Multi-Factor Alpha System Report

## Scope

This report validates the V1.3 multi-factor alpha pipeline:

Factors -> IC Scoring -> Normalization -> Weighting -> Portfolio Construction -> Risk Adjustment -> Backtest -> Attribution.

The run below is a deterministic local research example. It is not financial advice, not a live signal, and not connected to any broker.

## Example Factor Weights

- momentum_20d: 0.4166
- mean_reversion: 0.2878
- trend_strength: 0.2956

Bull-market regime adjustment was applied before alpha score construction, so momentum retained the largest weight.

## Backtest Metrics

- Total return: 13.26%
- Sharpe ratio: 22.38
- Sortino ratio: 342.43
- Max drawdown: 0.13%
- Calmar ratio: 2312.74
- Turnover: 0.0696

## Factor Return Contribution

- momentum_20d: 0.0044
- mean_reversion: 0.0027
- trend_strength: 0.0033

## Factor Risk Contribution

- momentum_20d: 0.0033
- mean_reversion: 0.0026
- trend_strength: 0.0018

## Factor Correlation Snapshot

| Factor | momentum_20d | mean_reversion | trend_strength |
| --- | ---: | ---: | ---: |
| momentum_20d | 1.0000 | 0.8348 | 0.9208 |
| mean_reversion | 0.8348 | 1.0000 | 0.7200 |
| trend_strength | 0.9208 | 0.7200 | 1.0000 |

## Interpretation

- The example alpha stack is dominated by momentum and trend, which is consistent with a bull regime.
- Correlation between factors is high, so production research should add diversification-aware factor pruning.
- The example return profile is intentionally smooth because the sample data is deterministic and low-noise.
- Causal alignment is preserved by shifting weights so portfolio returns start after signals are formed.

## Safety Boundary

- No broker API
- No real trading
- No auto order routing
- No external AI API
- No real-money execution

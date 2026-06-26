# V5 Robustness Report

## Multi-Asset Performance
- Asset count: 30
- Sectors: consumer, energy, financial, healthcare, industrial, materials, technology
- Total return: 1.0260
- Gross total return: 2.5325
- Sharpe: 0.8072
- Max drawdown: 0.2406
- Total cost: 0.5563

## Regime Breakdown
- bull: return=1.9232, sharpe=1.7006, drawdown=0.0924, observations=1036
- bear: return=-0.3410, sharpe=-1.2709, drawdown=0.3632, observations=334
- sideways: return=-0.0193, sharpe=0.0348, drawdown=0.2455, observations=685
- high_volatility: return=0.6591, sharpe=0.9688, drawdown=0.2278, observations=687
- low_volatility: return=0.2211, sharpe=0.6045, drawdown=0.1829, observations=687

## Stability Metrics
- Perturbation pct: 0.10
- Stability score: 0.00021051
- IC change proxy: 0.0130
- Sharpe change: 0.0064

## Monte Carlo / Bootstrap
- Alpha confidence interval: 0.0683 to 3.1221
- Worst case drawdown: 0.6441
- Median Sharpe: 0.8457

## Risk Summary
- Overfitting risk score: 41.51
- Alpha stability: HIGH
- Overfitting risk: MEDIUM
- Production readiness: YES
- Recommended action: Proceed to extended paper-trading shadow validation with no broker execution.

## Safety
- No broker connection
- No real trading
- No auto order routing
- No external AI API
- No profitability guarantee
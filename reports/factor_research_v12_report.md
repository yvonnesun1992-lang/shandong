# Quant Factor Research Report

## Factor Performance Table

| factor            |   ic_mean |    ic_std |    ic_ir |   ic_stability |   turnover_penalty |    score |
|:------------------|----------:|----------:|---------:|---------------:|-------------------:|---------:|
| breakout_strength |  0.936556 | 0.0757186 | 12.3689  |       1        |                  0 | 11.5842  |
| zscore_price      |  0.899979 | 0.0853418 | 10.5456  |       1        |                  0 |  9.4908  |
| momentum_20d      |  0.947887 | 0.101715  |  9.31905 |       1        |                  0 |  8.8334  |
| trend_strength    |  0.723134 | 0.35902   |  2.01419 |       0.851852 |                  0 |  1.24074 |

## Summary

- IC, IR, Sharpe proxy, and stability are calculated from local research data.
- Factor portfolio returns are simulated only; no broker connection or real trading is used.
- The analysis uses forward returns aligned after factor timestamps to avoid look-ahead bias.

## Selected Factors

breakout_strength, zscore_price, momentum_20d, trend_strength

## Example Portfolio Simulation

- Cumulative factor return: 52.4288%
- Factor weights: {'breakout_strength': 0.37189436083227867, 'zscore_price': 0.3046889999950178, 'momentum_20d': 0.2835842483680484, 'trend_strength': 0.03983239080465515}

## Safety Boundary

- No broker API
- No real trading
- No auto order routing
- No external AI API
- No real-money execution

# V5 Commercial Alpha Readiness

## Current Status

`V5.0-alpha-system` is now the current quantitative alpha core layer.

It can run a causal alpha pipeline from market data frames through:

Market Data -> Factor Matrices -> IC Scoring -> Alpha Scores -> Portfolio Weights -> Causal Backtest -> Metrics.

## What Is Commercially Useful Today

- Versioned V5 alpha-system entrypoints.
- Legacy V1.0-V1.3 research modules preserved for audit history.
- Time-safe factor research tests that prevent future backfill from returning.
- Multi-factor alpha model construction.
- Regime-aware factor weighting.
- Portfolio construction with no leverage and position caps.
- Causal backtest path that applies prior signals to next-period returns.
- Transaction cost and slippage adjusted validation metrics.
- Safety boundary stating no broker connection and no real-money execution.

## What Is Not Proven Yet

- Profitability is not proven.
- Live trading readiness is not proven.
- Real broker execution is not implemented.
- Production monitoring for live alpha decay is not implemented.
- Transaction costs, liquidity, borrow constraints, and tax effects are only partially represented.
- Survivorship-bias-free universe construction is not implemented.

## Required Evidence Before Commercial Claims

1. Multi-year backtest on realistic market data.
2. Strict train/test and walk-forward validation.
3. Out-of-sample factor decay analysis.
4. Transaction cost, slippage, and turnover stress tests.
5. Capacity and liquidity checks.
6. Risk-of-ruin and drawdown controls.
7. Paper trading forward test.
8. Production monitoring for alpha decay, execution drift, and data quality.
9. Multi-universe validation with stable walk-forward hit rate across sectors and regimes.

## Next Engineering Milestone

The next useful milestone is a V5 validation harness:

- Pull real historical data through the existing data loader.
- Run `quant_core_v5.pipeline.run_alpha_pipeline_from_market_data`.
- Save an auditable report with metrics, turnover, drawdown, and factor contribution.
- Compare train, test, and walk-forward periods.
- Compare multiple universes, not only one concentrated asset group.
- Keep broker execution disabled.

## Safety Boundary

- No broker API
- No real trading
- No auto order routing
- No external AI API
- No real-money execution
- No profitability guarantee

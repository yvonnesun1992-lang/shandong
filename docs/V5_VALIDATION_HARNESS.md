# V5 Validation Harness

## Purpose

The V5 validation harness moves the platform closer to commercial alpha validation.

It does not claim profitability. It creates auditable evidence for:

- train/test separation
- walk-forward validation
- causal portfolio returns
- no broker connection
- no real-money execution

## Entry Points

Python:

```python
from quant_core_v5.validation import run_validation_harness
```

CLI:

```bash
python scripts/run_v5_validation.py --symbols AAPL,MSFT,NVDA --start 2022-01-01
```

Multi-universe CLI:

```bash
python scripts/run_v5_validation_batch.py --universes "mega:AAPL,MSFT,NVDA;defensive:JNJ,PG,KO" --start 2021-01-01
```

## Output

The harness returns:

- train-period metrics
- test-period metrics
- walk-forward window metrics
- transaction cost and slippage adjusted metrics
- multi-universe robustness summary
- audit flags
- safety boundary flags

The CLI writes:

```text
reports/v5_alpha_validation_report.md
```

## Commercial Interpretation

A profitable test period is not enough for commercial claims.

Before marketing the system as profitable, the platform still needs:

- multi-year validation
- survivorship-bias-free universes
- transaction cost and slippage models
- liquidity and capacity checks
- forward paper trading
- monitoring for alpha decay

## Cost Model

V5 validation accepts:

- `transaction_cost_bps`
- `slippage_bps`

The backtest subtracts costs from returns based on portfolio turnover, and reports both gross and net return metrics.

## Safety Boundary

- No broker API
- No real trading
- No auto order routing
- No external AI API
- No real-money execution

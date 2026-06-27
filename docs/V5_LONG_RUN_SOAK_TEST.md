# V5.3 Long-Run Paper Trading Soak Test

V5.3 validates that the V5.2 runtime stability layer can survive longer paper-trading runs. It is not a strategy upgrade, alpha optimization, broker integration, or production deployment.

## Why This Exists

Short unit tests prove individual modules work. A soak test checks whether the runtime continues to behave under repeated ticks, checkpoint saves, injected faults, logging, health transitions, risk checks, and recovery paths.

## How To Run

```bash
python scripts/run_v53_soak_test.py --mode synthetic --ticks 1000
python scripts/run_v53_soak_test.py --mode synthetic --ticks 1000 --faults
python scripts/run_v53_soak_test.py --mode replay --ticks 1000
```

Outputs:

- console JSON summary
- `reports/v5_3_soak_test_report.md`
- `logs/runtime.jsonl`
- `data/runtime_state_checkpoint.json`

## Synthetic Market Modes

- `trend`: upward trending deterministic market
- `sideways`: range-like deterministic market
- `volatile`: high-volatility deterministic market
- `crash`: deterministic crash regime

Default symbols:

`AAPL, MSFT, NVDA, JPM, XOM, JNJ, PG, UNH, COST, META`

## Fault Injection

`runtime/fault_injection.py` can inject:

- signal error
- execution error
- missing market data
- price spike
- latency spike
- memory warning
- forced exception

Injected faults are controlled and must not crash the process.

## Consistency Validation

`runtime/consistency_validator.py` checks:

- cash is not invalidly negative
- positions are not invalidly negative
- equity equals cash plus position value
- PnL is not NaN
- checkpoint state contains basic portfolio state
- open orders have legal status

## Verdicts

- `PASS`: no critical errors, consistency passes, security scan passes, health is acceptable
- `WARNING`: run completed but health degraded or risk kill switch triggered
- `FAIL`: errors, consistency failure, or security scan failure

## Safety Boundary

- Paper trading only
- No broker connection
- No real orders
- No real account
- No real capital
- No payment system
- No alpha model changes
- No factor logic changes
- No new trading strategy


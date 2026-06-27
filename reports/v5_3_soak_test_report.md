# V5.3 Long-Run Paper Trading Soak Test Report

## Test Configuration
- Mode: synthetic
- Market regime: trend
- Symbols: AAPL, COST, JNJ, JPM, META, MSFT, NVDA, PG, UNH, XOM
- Fault injection: True

## Runtime Summary
- Duration seconds: 4.9359
- Ticks processed: 1000
- Final equity: 103388.71269627578
- Max drawdown: 0.029107858347110774
- Error count: 11
- Restart count: 0
- Checkpoint count: 1

## Health Status Timeline
- Final health status: DEGRADED

## Mode Transition Summary
- Final mode: SAFE_MODE

## Risk Trigger Summary
- Risk kill switch triggered: False

## Consistency Validation
- Consistent: True
- Checks: cash_non_negative, positions_non_negative, equity_identity, pnl_not_nan, checkpoint_basic_state, open_order_status
- Errors: []

## Sensitive Data Scan
- Safe: True
- Findings: []

## Final verdict
WARNING

## Safety
- Paper trading only
- No broker connection
- No real trading
- No real account
- No payment system
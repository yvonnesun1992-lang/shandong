# V5.6 Live Paper Trading Staging

V5.6 introduces a live market data paper trading staging layer.

## Goal

The goal is to validate this loop:

```text
Live Market Data Adapter -> Market Data Normalizer -> V5 Runtime Shape -> Paper Broker -> Portfolio / PnL -> Monitoring API / Dashboard
```

This stage is not real trading and is not production live trading.

## Live Paper Trading

Live paper trading means the system can consume market data that behaves like live quotes while all orders, fills, cash, positions, and PnL remain simulated.

## Live Market Data vs Real Trading

Live market data reads prices. Real trading sends orders to a broker. V5.6 only reads prices and only uses paper execution.

## Modes

```text
mock_live
yfinance_polling
```

`mock_live` is the default. `yfinance_polling` is optional and falls back to `mock_live` if market data cannot be fetched.

## Run The CLI

```bash
python scripts/run_v56_live_paper_staging.py --mode mock_live --ticks 20
python scripts/run_v56_live_paper_staging.py --mode yfinance_polling --ticks 5
python scripts/run_v56_live_paper_staging.py --mode mock_live --once
```

Outputs:

```text
reports/v5_6_live_paper_staging_report.md
logs/runtime.jsonl
data/runtime_state_checkpoint.json
```

## API Endpoints

```text
GET /api/v5/live-paper/status
GET /api/v5/live-paper/config
GET /api/v5/live-paper/latest-tick
GET /api/v5/live-paper/summary
```

## Frontend Page

```text
web/frontend/app/v5-live-paper/page.tsx
```

The page shows staging status, safety boundaries, provider mode, symbols, latest tick, paper portfolio, risk state, health state, warnings, and errors.

## Safety Boundary

- No broker connection
- No real orders
- No real account
- No real money
- No payment integration
- No production live trading
- No alpha model changes
- No factor logic changes
- No new trading strategy
- No external AI API

## Known Limits

- The default mode is mock live market data
- Optional yfinance polling is quote-only and can fall back to mock data
- No broker integration exists in this stage
- Runtime scheduling is local and bounded by tick count

## Next Step

The next safe stage is broker integration planning: define interfaces and controls before any real broker connection exists.

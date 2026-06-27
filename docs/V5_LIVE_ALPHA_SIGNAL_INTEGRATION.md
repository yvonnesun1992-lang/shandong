# V5.7 Live Alpha Signal Integration

V5.7 upgrades live paper staging from market-data heartbeat validation to V5 alpha signal driven paper trading.

## Goal

The target loop is:

```text
Live Tick -> Feature Window -> Existing V5 Alpha Model -> BUY / SELL / HOLD Signal -> Paper Order -> Paper Execution -> Monitoring
```

## Live Paper Staging vs Live Alpha Paper

V5.6 validated that market-data-like ticks can flow into a paper trading staging system. V5.7 adds the alpha signal adapter so paper orders can be generated from V5 alpha signals rather than a fixed heartbeat order.

## Why Replace Heartbeat Order

Heartbeat orders prove plumbing, but they are not signal driven. V5.7 removes the fixed observation order from the staging runner and routes orders through:

```text
LiveAlphaSignalAdapter -> SignalToOrderConverter -> RiskGate -> PaperBroker
```

## Feature Buffer

`LiveFeatureBuffer` stores recent ticks by symbol. It drops invalid ticks, rejects non-positive close prices, keeps a bounded rolling window, and returns DataFrame windows sorted by timestamp.

## Alpha Signal Adapter

`LiveAlphaSignalAdapter` reuses the existing V5 alpha model wrapper. If the feature window is not ready or the alpha model cannot score the frame, it returns a safe HOLD signal with paper-only flags.

## Signal To Order

The existing `SignalToOrderConverter` turns BUY and SELL signals into paper orders. HOLD creates no order. The risk gate runs before simulated execution.

## Run The CLI

```bash
python scripts/run_v57_live_alpha_paper.py --mode mock_live --ticks 100
python scripts/run_v57_live_alpha_paper.py --mode yfinance_polling --ticks 20
python scripts/run_v57_live_alpha_paper.py --mode mock_live --once
```

## API Endpoints

```text
GET /api/v5/live-alpha/status
GET /api/v5/live-alpha/latest-signals
GET /api/v5/live-alpha/summary
GET /api/v5/live-alpha/buffer-status
```

## Frontend Page

```text
web/frontend/app/v5-live-alpha/page.tsx
```

## Safety Boundary

- No broker connection
- No real orders
- No real account
- No real money
- No payment integration
- Not production live trading
- No alpha model changes
- No factor logic changes
- No new trading strategy

## Known Limits

- Default data mode remains mock live
- Optional yfinance polling is market-data-only and can fall back to mock live data
- Alpha signals are intended for paper execution only

## Next Step

The next safe stage is broker integration planning, with interface design and risk controls before any real broker connection exists.

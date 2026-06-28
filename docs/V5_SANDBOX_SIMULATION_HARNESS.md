# V5.11 Sandbox Simulation Harness

V5.11 adds a local-only sandbox simulation harness. It models a future broker
sandbox order lifecycle without connecting to any broker, sandbox API, real
account, external network, payment service, or live trading system.

## Goal

The goal is to rehearse the operational path between paper orders and a future
broker sandbox connector:

1. Live or mock tick
2. Alpha signal placeholder
3. Order intent
4. Manual approval simulated
5. Local simulation broker
6. Simulated lifecycle state changes
7. Simulated fill, reject, cancel, latency, or disconnect
8. Local audit summary
9. Monitoring and report payload

## Why Local Simulation First

Broker sandbox environments still require credentials, order routing, and
external system behavior. V5.11 deliberately keeps that boundary closed and
creates a deterministic local harness first so lifecycle, monitoring, audit,
and rollback behavior can be reviewed before any external connector work.

## Simulated Sandbox Account

`sandbox_sim/simulated_sandbox_account.py` tracks local-only cash, positions,
buying power, realized PnL, unrealized PnL, and equity. It does not read a real
account, real balance, or real positions.

## Simulated Sandbox Broker

`sandbox_sim/sandbox_simulation_broker.py` accepts order intents and creates
local simulated orders. It supports:

- full fill
- partial fill
- reject
- cancel
- latency
- disconnect
- insufficient cash
- invalid symbol
- risk rejected

No external SDK, HTTP client, broker endpoint, or sandbox order route is used.

## Order Lifecycle Simulator

`sandbox_sim/order_lifecycle_simulator.py` supports local transitions:

- `NEW -> ACCEPTED -> FILLED`
- `NEW -> ACCEPTED -> PARTIALLY_FILLED -> FILLED`
- `NEW -> REJECTED`
- `NEW -> ACCEPTED -> CANCELED`
- `NEW -> ACCEPTED -> EXPIRED`

Real broker states such as `LIVE_SUBMITTED`, `REAL_ORDER_READY`, and
`BROKER_ACCEPTED_REAL` are blocked.

## Fault Simulation

`sandbox_sim/sandbox_simulation_faults.py` models local faults:

- broker disconnect
- network latency
- duplicate order acknowledgement
- missing fill report
- stale market price
- partial fill stuck
- cancel reject
- risk reject

These faults affect only the local simulation broker.

## CLI

```bash
python scripts/run_v511_sandbox_simulation.py --scenario full_fill --ticks 100
python scripts/run_v511_sandbox_simulation.py --scenario partial_fill --ticks 100
python scripts/run_v511_sandbox_simulation.py --scenario reject --ticks 100
python scripts/run_v511_sandbox_simulation.py --scenario disconnect --ticks 50
python scripts/run_v511_sandbox_simulation.py --scenario latency --ticks 50
```

The CLI writes `reports/v5_11_sandbox_simulation_harness_report.md`.

## API Endpoints

- `GET /api/v5/sandbox-sim/status`
- `GET /api/v5/sandbox-sim/account`
- `GET /api/v5/sandbox-sim/orders`
- `GET /api/v5/sandbox-sim/fills`
- `GET /api/v5/sandbox-sim/scenarios`
- `GET /api/v5/sandbox-sim/summary`

## Frontend Page

`web/frontend/app/v5-sandbox-sim/page.tsx` shows local simulation status,
safety boundary, simulated account, simulated orders, simulated fills, fault
simulation, lifecycle summary, and final verdict.

## Safety Boundary

- Current mode is local sandbox simulation only.
- Sandbox API connection is disabled.
- Real broker connection is disabled.
- Real order submission is disabled.
- Real capital movement is disabled.
- Production live trading is disabled.
- Alpha model, factor logic, and strategy logic are unchanged.

## Known Limitations

V5.11 is not a broker connector. It does not validate a provider SDK, broker
credential vault, exchange-specific order fields, broker-side rejects, or real
network latency. Those are future planning items only.

## Next Step

The next safe step is real broker sandbox connector planning, still behind
credential isolation, manual approval, kill switch, audit logging, and rollback
requirements.

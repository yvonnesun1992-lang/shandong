# V5.12 Sandbox Simulation Robustness Suite

V5.12 adds a local-only robustness suite for the V5.11 sandbox simulation
harness. It does not connect to a broker, sandbox API, real account, external
network, payment service, or production live trading system.

## Goal

The goal is to validate the local sandbox simulation under broader operating
conditions:

- scenario matrix
- multi-symbol simulation
- combined fault testing
- long-run robustness
- account, order, fill, and audit consistency validation
- robustness API, report, CLI, and frontend page

## Scenario Matrix

The matrix includes base scenarios such as full fill, partial fill, reject,
cancel, latency, disconnect, insufficient cash, invalid symbol, and risk
rejected. It also includes combined local fault scenarios such as latency plus
partial fill, disconnect plus missing fill report, duplicate acknowledgement
plus partial fill, and partial fill stuck plus manual reject.

## Multi-symbol Simulation

`sandbox_sim/multi_symbol_simulator.py` runs deterministic local simulations
for AAPL, MSFT, NVDA, SPY, and QQQ. Each symbol receives a local simulated
order lifecycle and contributes to the summary payload.

## Fault Combination Testing

`sandbox_sim/fault_combination_runner.py` combines local-only faults such as
network latency, stale market price, missing fill report, cancel reject, and
risk reject. It does not call a network or broker.

## Consistency Validator

`sandbox_sim/robustness_consistency_validator.py` checks account values,
allowed order statuses, fill quantities, terminal order consistency, audit
coverage, and the no-real-broker boundary.

## Long-run Robustness

`sandbox_sim/long_run_robustness_runner.py` runs scenario batches with a
deterministic seed and reports pass, warning, and fail counts.

## CLI

```bash
python scripts/run_v512_sandbox_robustness.py --ticks 1000 --symbols AAPL,MSFT,NVDA,SPY,QQQ
python scripts/run_v512_sandbox_robustness.py --scenario full_fill --ticks 500
python scripts/run_v512_sandbox_robustness.py --scenario partial_fill --ticks 500
python scripts/run_v512_sandbox_robustness.py --scenario reject --ticks 500
python scripts/run_v512_sandbox_robustness.py --all-scenarios --ticks 1000
```

The CLI writes `reports/v5_12_sandbox_simulation_robustness_report.md`.

## API Endpoints

- `GET /api/v5/sandbox-robustness/status`
- `GET /api/v5/sandbox-robustness/scenario-matrix`
- `GET /api/v5/sandbox-robustness/multi-symbol`
- `GET /api/v5/sandbox-robustness/fault-combinations`
- `GET /api/v5/sandbox-robustness/long-run`
- `GET /api/v5/sandbox-robustness/summary`

## Frontend Page

`web/frontend/app/v5-sandbox-robustness/page.tsx` shows robustness status,
safety boundary, scenario matrix, multi-symbol simulation, fault combinations,
long-run robustness, consistency validation, and final verdict.

## Safety Boundary

- Current mode is local sandbox simulation robustness only.
- Sandbox API connection is disabled.
- Real broker connection is disabled.
- Real order submission is disabled.
- Real capital movement is disabled.
- Production live trading is disabled.
- Alpha model, factor logic, and strategy logic are unchanged.

## Known Limitations

V5.12 validates local deterministic simulation behavior only. It does not
validate a real broker sandbox connector, credential vault, exchange-specific
order fields, broker-side rejects, or live network behavior.

## Next Step

The next safe step is still real broker sandbox connector planning, behind
credential isolation, manual approval, kill switch, audit logging, and rollback
requirements.

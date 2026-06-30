# V5.36 Sandbox Read-Only Connector Stability Gate

V5.36 adds a local-only stability gate for the read-only connector path. It aggregates V5.34 mock replay evidence and V5.35 fault injection evidence, then keeps the final gate blocked by design.

## Gate Inputs

- V5.34 read-only mock replay evidence
- V5.35 read-only fault injection evidence
- Redaction stability
- Schema stability
- Audit stability
- Order path stability
- Safety validation

## Decision

The decision is always `STABILITY_GATE_BLOCKED` in V5.36.

Passing replay evidence, passing fault evidence, or simulated approval cannot unlock:

- Sandbox API
- Credential access
- Account reads
- Balance reads
- Position reads
- Order preview
- Order submission
- Real money

## API

- `GET /api/v5/read-only-stability-gate/status`
- `GET /api/v5/read-only-stability-gate/replay-evidence`
- `GET /api/v5/read-only-stability-gate/fault-evidence`
- `GET /api/v5/read-only-stability-gate/redaction`
- `GET /api/v5/read-only-stability-gate/schema`
- `GET /api/v5/read-only-stability-gate/audit`
- `GET /api/v5/read-only-stability-gate/order-path`
- `GET /api/v5/read-only-stability-gate/decision`
- `GET /api/v5/read-only-stability-gate/safety`
- `GET /api/v5/read-only-stability-gate/summary`

## CLI

```bash
python scripts/run_v536_read_only_stability_gate.py
python scripts/run_v536_read_only_stability_gate.py --provider alpaca
python scripts/run_v536_read_only_stability_gate.py --provider ibkr
python scripts/run_v536_read_only_stability_gate.py --check replay
python scripts/run_v536_read_only_stability_gate.py --check fault
python scripts/run_v536_read_only_stability_gate.py --check redaction
python scripts/run_v536_read_only_stability_gate.py --check schema
python scripts/run_v536_read_only_stability_gate.py --check order-path
python scripts/run_v536_read_only_stability_gate.py --check decision
python scripts/run_v536_read_only_stability_gate.py --check safety
```

## Safety Boundary

- No real broker API
- No broker sandbox API
- No provider portal access
- No real or sandbox account creation
- No credential read
- No account read
- No balance read
- No position read
- No order preview
- No order submission
- No real money
- No external network
- No alpha model changes
- No factor logic changes
- No new trading strategy

V5.36 is stability gate evidence only, not a production trading system.

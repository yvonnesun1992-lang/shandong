# V5.35 Sandbox Read-Only Connector Fault Injection

V5.35 adds a local-only fault injection suite for the V5.34 read-only mock replay layer.

This stage intentionally injects malformed and unsafe local mock payloads so validators can prove they block or warn on failure paths. It does not connect to a broker, sandbox API, provider portal, or external network.

## Fault Cases

- Redaction failure
- Malformed account snapshot
- Malformed balance snapshot
- Malformed position snapshot
- Stale snapshot
- Rate limit error
- Audit write failure
- Unexpected raw provider payload placeholder
- Unexpected account reference exposure
- Unexpected numeric balance or position exposure
- Unexpected order preview or order submission path

## Components

- Fault payload catalog
- Fault schema validator
- Redaction failure detector
- Stale snapshot detector
- Audit failure simulator
- Rate limit fault simulator
- Order path intrusion detector
- Fault injection runner
- Safety validator
- Report, CLI, API, and frontend page

## API

- `GET /api/v5/read-only-fault-injection/status`
- `GET /api/v5/read-only-fault-injection/payloads`
- `GET /api/v5/read-only-fault-injection/schema`
- `GET /api/v5/read-only-fault-injection/redaction`
- `GET /api/v5/read-only-fault-injection/stale`
- `GET /api/v5/read-only-fault-injection/audit-failure`
- `GET /api/v5/read-only-fault-injection/rate-limit`
- `GET /api/v5/read-only-fault-injection/order-intrusion`
- `GET /api/v5/read-only-fault-injection/run`
- `GET /api/v5/read-only-fault-injection/safety`
- `GET /api/v5/read-only-fault-injection/summary`

## CLI

```bash
python scripts/run_v535_read_only_fault_injection.py
python scripts/run_v535_read_only_fault_injection.py --provider alpaca
python scripts/run_v535_read_only_fault_injection.py --provider ibkr
python scripts/run_v535_read_only_fault_injection.py --check redaction
python scripts/run_v535_read_only_fault_injection.py --check stale
python scripts/run_v535_read_only_fault_injection.py --check order-intrusion
python scripts/run_v535_read_only_fault_injection.py --check safety
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

V5.35 is fault injection only, not a production trading system.

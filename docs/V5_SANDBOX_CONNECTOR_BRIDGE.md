# V5.16 Sandbox Connector Bridge

V5.16 adds a sandbox connector bridge abstraction layer between the V5.15 broker adapter skeleton and any future sandbox connector. It does not connect to a sandbox API, broker API, payment system, or production trading service.

## What It Adds

- Sandbox bridge core.
- Request transformation layer.
- Response normalization layer.
- Error translation layer.
- Retry orchestration layer.
- Idempotency enforcement layer.
- Simulated sandbox session lifecycle.
- Sandbox routing layer.
- Bridge safety gate.
- Report and CLI.
- API endpoints under `/api/v5/sandbox-bridge/*`.
- Frontend page at `/v5-sandbox-bridge`.

## Boundary

- No real broker connection.
- No sandbox API connection.
- No real order routing.
- No real account read.
- No real position read.
- No real balance read.
- No payment flow.
- No production trading.
- No alpha model changes.
- No factor logic changes.
- No new strategy.

## CLI

```bash
python scripts/run_v516_sandbox_bridge.py --test route
python scripts/run_v516_sandbox_bridge.py --test transform
python scripts/run_v516_sandbox_bridge.py --test normalize
```

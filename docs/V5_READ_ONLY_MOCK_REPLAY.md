# V5.34 Sandbox Read-Only Connector Mock Replay

V5.34 adds a local-only mock replay layer for the V5.33 read-only connector blueprint.

This stage is intentionally limited to static, redacted payload replay. It does not connect to any provider or enable any runtime data access.

## What It Includes

- Local placeholder payload catalog
- Account, balance, position, and error snapshot mock payloads
- Schema validation for placeholder payloads
- Redaction validation for balance and position values
- Replay runner with audit events
- Safety validator
- API endpoints under `/api/v5/read-only-mock-replay/*`
- Frontend status page
- CLI checks via `scripts/run_v534_read_only_mock_replay.py`

## Safety Boundary

- No real broker connection
- No sandbox API call
- No credential read
- No account read
- No balance read
- No position read
- No order preview
- No order submission
- No real money
- No raw provider payload
- No provider endpoint URL

## CLI

```bash
python scripts/run_v534_read_only_mock_replay.py
python scripts/run_v534_read_only_mock_replay.py --provider alpaca
python scripts/run_v534_read_only_mock_replay.py --provider ibkr
python scripts/run_v534_read_only_mock_replay.py --check schema
python scripts/run_v534_read_only_mock_replay.py --check redaction
python scripts/run_v534_read_only_mock_replay.py --check safety
```

## API

- `GET /api/v5/read-only-mock-replay/status`
- `GET /api/v5/read-only-mock-replay/payloads`
- `GET /api/v5/read-only-mock-replay/schema`
- `GET /api/v5/read-only-mock-replay/redaction`
- `GET /api/v5/read-only-mock-replay/run`
- `GET /api/v5/read-only-mock-replay/audit`
- `GET /api/v5/read-only-mock-replay/safety`
- `GET /api/v5/read-only-mock-replay/summary`

## Current Status

V5.34 is a mock replay readiness layer only. It prepares local evidence for future review while keeping every real provider path disabled.

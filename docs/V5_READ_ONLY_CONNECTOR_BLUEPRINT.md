# V5.33 Sandbox Dry-Run Read-Only Connector Blueprint

V5.33 defines a future sandbox read-only connector design. It is blueprint material only.

It does not connect to a broker, call a sandbox API, read credentials, read accounts, read balances, read positions, submit orders, or use real funds.

## Scope

- Read-only scope definition
- Credential scope
- Account snapshot schema
- Balance snapshot schema
- Position snapshot schema
- Redaction policy
- Rate limit policy
- Audit policy
- Read-only safety validation

## Boundary

- No real broker API
- No broker sandbox API
- No provider portal access
- No credential read or storage
- No account, balance, or position read
- No real or sandbox order submission
- No real funds
- No external network access
- No raw provider payload storage
- No alpha, factor, or strategy changes

## Status

The current phase is blueprint-only. All runtime and read paths remain disabled.

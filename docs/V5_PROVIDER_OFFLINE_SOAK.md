# V5.25 Provider Sandbox Offline Soak & Stability Gate

V5.25 adds an offline soak and stability gate for the selected provider sandbox connector path.

This phase is offline soak only. It validates replay stability, fault recovery stability, idempotency stability, state-machine stability, audit consistency, memory growth placeholders, error budget checks, scenario coverage, safety boundary stability, and readiness gate behavior.

## What It Includes

- Offline soak scenario plan
- Deterministic local event generator
- Offline soak runner
- Stability metrics
- Stability gate
- Scenario coverage validator
- Safety validator
- CLI and report generation
- API endpoints under `/api/v5/provider-offline-soak/*`
- V5 Offline Soak frontend page

## Safety Boundary

- No real broker connection
- No sandbox API connection
- No provider portal access
- No credential creation
- No account read
- No order submission
- No real money
- No external network calls
- No raw provider payload storage
- No alpha, factor, or strategy changes

This is not a production trading system.

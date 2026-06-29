# V5.19 Broker Sandbox Provider Selection

V5.19 is a provider selection and account preparation layer only. It compares possible future broker sandbox providers and lists the account, API, market data, and compliance work required before any future sandbox stage.

## Scope

- Defines the static provider universe: Alpaca, IBKR, Futu, Tiger, and Schwab.
- Adds capability and risk matrices.
- Adds account, API permission, market data permission, and compliance checklists.
- Adds provider ranking and a recommended provider based on static scoring.
- Adds API endpoints under `/api/v5/provider-selection/*`.
- Adds a frontend page at `/v5-provider-selection`.
- Adds a CLI report generator at `scripts/run_v519_provider_selection.py`.

## Boundaries

- No real broker connection.
- No broker sandbox API connection.
- No account reads.
- No order submission.
- No real funds.
- No credential storage.
- No OAuth.
- No external network requests.
- No alpha model, factor logic, or strategy changes.

## Current Verdict

The system remains paper trading only. Provider ranking is metadata-based and does not imply readiness to connect to any broker.

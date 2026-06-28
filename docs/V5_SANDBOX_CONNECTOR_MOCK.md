# V5.14 Sandbox Connector Mock Implementation

V5.14 adds a local mock implementation for the V5.13 sandbox connector contract. It is designed for product demos, API integration tests, frontend status views, and safe scenario validation.

## What It Includes

- Mock connector status configuration.
- Local in-memory order state store.
- Mock order lifecycle policy.
- Mock response factory.
- Mock connector scenario runner.
- Mock connector safety validator.
- Mock connector report and CLI.
- API endpoints under `/api/v5/sandbox-connector-mock/*`.
- Frontend page at `/v5-sandbox-connector-mock`.

## Safety Boundary

- No real broker connection.
- No sandbox API connection.
- No sandbox order routing.
- No real order routing.
- No real account read.
- No real position read.
- No real balance read.
- No payment flow.
- No production live trading.
- No alpha model changes.
- No factor logic changes.
- No new strategy.

## Supported Mock Scenarios

- accepted
- filled
- partial_fill
- rejected
- duplicate
- rate_limited
- cancel_accepted
- cancel_rejected
- provider_unavailable
- timeout
- manual_approval_required
- kill_switch_active

## CLI

```bash
python scripts/run_v514_sandbox_connector_mock.py --scenario accepted
python scripts/run_v514_sandbox_connector_mock.py --all-scenarios
```

The CLI writes `reports/v5_14_sandbox_connector_mock_report.md`.

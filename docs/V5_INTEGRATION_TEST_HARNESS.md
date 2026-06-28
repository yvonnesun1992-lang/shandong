# V5.17 Sandbox Connector Integration Test Harness

V5.17 adds an end-to-end integration test harness for the simulated future broker path. It validates Alpha Signal to Paper Trading Engine to Manual Approval to Broker Adapter Skeleton to Mock Connector to Sandbox Bridge to execution simulation, monitoring, risk, and audit outputs.

## What It Adds

- Integration test core runner.
- Layered pipeline tester.
- Failure injection engine.
- Cross-layer consistency validator.
- Integration scenario matrix.
- Integration test orchestrator.
- Integration safety gate.
- Report and CLI.
- API endpoints under `/api/v5/integration-test/*`.
- Frontend page at `/v5-integration-test`.

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
python scripts/run_v517_integration_test_harness.py --scenario normal_flow
python scripts/run_v517_integration_test_harness.py --scenario full_failure_chain
python scripts/run_v517_integration_test_harness.py --all
```

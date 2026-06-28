# V5.10 Broker Sandbox Readiness Planning

V5.10 adds a planning-only broker sandbox readiness layer. It does not connect
to a sandbox API, connect to a real broker, read credentials, submit sandbox
orders, submit real orders, or access real capital.

## Goal

The goal is to prepare the checklist and safety model required before any
future broker sandbox work:

- sandbox provider readiness
- credential isolation design
- sandbox order lifecycle plan
- sandbox safety checklist
- sandbox rollback plan
- sandbox readiness API and report
- V5 Sandbox frontend page

## Why Readiness Planning First

Sandbox order routing still crosses a broker boundary. Before even a simulated
broker environment is connected, the system must show that credentials,
operator approval, risk controls, audit logging, rollback, and monitoring are
designed and separated from the existing paper-only runtime.

## Sandbox Provider Plan

`sandbox/sandbox_provider_plan.py` lists future provider plans:

- alpaca_sandbox_planned
- ibkr_paper_planned
- futu_sim_planned
- tiger_sim_planned
- schwab_sandbox_planned

No provider SDK is imported, no external API is connected, and no credential is
loaded.

## Credential Isolation Plan

`sandbox/credential_isolation_plan.py` states:

- credentials must not be committed
- credentials must not be stored in plaintext
- credentials must not be logged
- credentials must be loaded from an external vault in the future
- local `.env` is only a future development placeholder
- CI must not expose broker credentials
- logs must be sanitized
- frontend must never receive credentials

## Sandbox Order Lifecycle Plan

`sandbox/sandbox_order_lifecycle_plan.py` documents the future lifecycle:

1. alpha_signal_generated
2. paper_order_created
3. risk_gate_checked
4. manual_approval_required
5. sandbox_order_preview_created
6. sandbox_order_submission_planned
7. broker_response_planned
8. audit_event_recorded
9. kill_switch_checked

Current order submission remains disabled and rejected by default.

## Safety Checklist

`sandbox/sandbox_safety_checklist.py` checks for:

- manual approval gate
- broker safety gate
- kill switch
- audit trail
- credential isolation plan
- order mapping plan
- rollback plan
- monitoring
- paper trading baseline
- live alpha paper baseline

Current readiness remains false for sandbox connection and sandbox orders.

## Rollback Plan

`sandbox/sandbox_rollback_plan.py` documents:

- disable sandbox connection
- disable sandbox order submission
- switch to paper-only mode
- clear pending sandbox order queue
- freeze manual approval queue
- notify operator placeholder
- write audit event
- restore last safe checkpoint
- generate rollback report

No external notification service or broker cancel API is called.

## API Endpoints

- `GET /api/v5/sandbox/status`
- `GET /api/v5/sandbox/provider-plan`
- `GET /api/v5/sandbox/credential-policy`
- `GET /api/v5/sandbox/order-lifecycle`
- `GET /api/v5/sandbox/safety-checklist`
- `GET /api/v5/sandbox/rollback-plan`

These endpoints return readiness planning only and do not expose credentials,
local absolute paths, or external account details.

## Frontend Page

`web/frontend/app/v5-sandbox/page.tsx` shows:

- Sandbox Readiness Status
- Safety Boundary
- Provider Plan
- Credential Isolation Policy
- Sandbox Order Lifecycle
- Safety Checklist
- Rollback Plan
- Missing Requirements
- Final Verdict

The page has safe fallback behavior when the backend is unavailable.

## CLI

Run:

```bash
python scripts/run_v510_broker_sandbox_readiness.py
```

It writes:

```text
reports/v5_10_broker_sandbox_readiness_report.md
```

## Future Requirements Before Real Sandbox

- external vault integration
- sandbox-only credential scope
- CI credential masking policy
- broker sandbox certification
- operator approval drill
- kill switch drill
- rollback drill
- separate production readiness review

## Safety Boundary

- No broker sandbox API connection
- No real broker connection
- No sandbox order submission
- No real order submission
- No real account access
- No real capital
- No payment system
- No production live trading
- No alpha model changes
- No factor logic changes
- No new trading strategy

## Known Limitations

V5.10 is readiness planning only. It is intentionally not ready for real broker
sandbox connectivity or sandbox order submission.

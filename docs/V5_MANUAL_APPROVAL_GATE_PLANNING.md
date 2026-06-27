# V5.9 Manual Approval Gate Planning

V5.9 adds a planning-only manual approval gate before any future broker order
release. It does not connect to a broker, submit real orders, access real
capital, or implement a real production approval system.

## Goal

The goal is to document and expose the future manual approval shape:

- approval request model
- approval state machine
- reject-by-default policy
- local audit trail
- approval risk summary
- approval readiness API and report
- V5 Approval frontend page

## Why Manual Approval Before Real Orders

Future broker order release would be a high-risk operation. A manual approval
gate must exist before any sandbox or live broker path because paper order
intent must be reviewed, risk-checked, audited, and rejected by default until a
separate production safety review approves otherwise.

## Approval Request Model

`approval/approval_request.py` defines a safe approval request with:

- approval id
- paper order intent id
- symbol, side, quantity, order type
- notional value
- signal source and strength
- risk summary
- state and review metadata

It intentionally excludes broker account references, real broker order
identifiers, secrets, and external account data.

## State Machine

Allowed flow:

```text
DRAFT -> PENDING_REVIEW -> APPROVED_SIMULATED / REJECTED / EXPIRED
```

Blocked states:

- `AUTO_APPROVED`
- `LIVE_APPROVED`
- `REAL_ORDER_READY`

`APPROVED_SIMULATED` only means a simulated paper review passed. It never
enables real orders.

## Reject-by-default Policy

All order intents are rejected or held for review by default. Real order
attempts are always rejected in V5.9.

## Audit Trail

`approval/approval_audit_trail.py` writes local JSONL events:

- approval_created
- approval_reviewed
- approval_rejected
- approval_expired
- real_order_attempt_rejected

Audit records are local-only and do not store secrets, broker credentials,
real account details, or real broker order identifiers.

## Risk Summary

`approval/approval_risk_summary.py` builds a paper-only review summary:

- symbol
- side
- quantity
- estimated notional
- signal strength
- position limit check
- drawdown check
- daily loss check
- broker connected false
- real orders disabled
- real money disabled

## API Endpoints

- `GET /api/v5/approval/status`
- `GET /api/v5/approval/readiness`
- `GET /api/v5/approval/policy`
- `GET /api/v5/approval/audit-summary`

These endpoints return planning data only and do not expose secrets, local
absolute paths, or external account details.

## Frontend Page

`web/frontend/app/v5-approval/page.tsx` shows:

- Manual Approval Gate Status
- Safety Boundary
- Approval Policy
- Approval State Machine
- Reject-by-default Policy
- Audit Trail Summary
- Missing Production Requirements
- Final Verdict

The page has safe fallback behavior when the backend is unavailable.

## CLI

Run:

```bash
python scripts/run_v59_manual_approval_gate.py
```

It writes:

```text
reports/v5_9_manual_approval_gate_report.md
```

## Future Requirements Before Broker Sandbox

- real human identity and role review
- dual approval workflow
- broker sandbox certification
- immutable audit storage
- independent kill switch
- legal and operational approval
- separate production readiness review

## Safety Boundary

- No real broker connection
- No real order submission
- No real account access
- No real position access
- No real balance access
- No real capital
- No payment system
- No production live trading
- No alpha model changes
- No factor logic changes
- No new trading strategy

## Known Limitations

V5.9 is planning only. It is intentionally not ready for real broker order
approval or production live trading.

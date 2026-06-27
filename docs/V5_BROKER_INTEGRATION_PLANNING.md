# V5.8 Broker Integration Planning

V5.8 adds a broker integration planning layer for the V5 paper trading stack.
It does not connect to a broker, read a real account, read real positions,
submit real orders, or access real capital.

## Goal

The goal is to document and expose the future broker integration shape before
any live broker work begins:

- Broker adapter interface
- Planned broker adapter
- Paper order mapping plan
- Account and position mapping plan
- Broker safety gate
- Broker readiness API and report
- V5 Broker frontend page

## Why Planning First

Broker integration is a high-risk boundary. The system must prove that paper
trading, risk gates, order mapping, account mapping, and operational review
are separated before any external broker work can be considered.

## Broker Adapter Interface

`broker/broker_adapter_interface.py` defines the future adapter methods:

- `get_account()`
- `get_positions()`
- `submit_order(order)`
- `cancel_order(order_id)`
- `get_order_status(order_id)`

The interface is documentation-only in V5.8. Default behavior raises
`NotImplementedError` and does not connect externally.

## Planned Broker Adapter

`broker/planned_broker_adapter.py` provides a safe planned adapter:

- account calls return planned-only metadata
- positions return an empty list
- order submission is always rejected
- cancellation and status calls return planned-only responses

Every response makes the boundary explicit:

- `broker_connected: false`
- `real_order_submitted: false`
- `paper_trading: true`

## Order Mapping Plan

`broker/order_mapping_plan.py` documents future paper-order-to-broker-order
mapping fields:

- symbol
- side
- quantity
- order type
- time in force
- market and limit order shape

The mapping is not active. It does not create real broker orders and remains
rejected by default.

## Safety Gate

`broker/broker_safety_gate.py` validates the current safety posture:

- broker connection must remain false
- real orders must remain disabled
- real money must remain disabled
- manual approval is required before future broker work
- kill switch is required before future broker work
- position limits are required before future broker work

Any real-order attempt is rejected.

## API Endpoints

- `GET /api/v5/broker/status`
- `GET /api/v5/broker/readiness`
- `GET /api/v5/broker/safety`
- `GET /api/v5/broker/order-mapping`

These endpoints return planning data only. They do not require broker access
and do not expose credentials, local paths, or external account details.

## Frontend Page

`web/frontend/app/v5-broker/page.tsx` shows:

- Broker Integration Status
- Safety Boundary
- Planned Provider
- Execution Mode
- Broker Adapter Interface
- Order Mapping Plan
- Required Safety Gates
- Missing Production Requirements
- Final Verdict

The page has safe fallback behavior when the backend is unavailable.

## CLI

Run:

```bash
python scripts/run_v58_broker_integration_planning.py
```

It writes:

```text
reports/v5_8_broker_integration_planning_report.md
```

## Future Requirements Before Broker Work

- manual approval workflow
- independent kill switch
- position and notional limits
- sandbox certification
- credential vault design outside the repository
- legal and operational review
- separate security review
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

V5.8 is planning only. It is intentionally not ready for live broker execution.

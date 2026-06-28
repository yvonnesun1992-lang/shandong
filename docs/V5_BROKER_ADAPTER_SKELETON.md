# V5.15 Broker Adapter Skeleton + Sandbox Bridge

V5.15 defines the broker adapter skeleton layer for future provider integrations. It does not connect to any broker, sandbox API, payment system, or production trading service.

## What It Adds

- Broker adapter base class.
- Adapter registry and factory.
- IBKR and Alpaca skeleton adapters.
- Futu, Tiger, and Schwab skeleton adapters.
- Mock adapter wrapper for the V5.14 mock connector.
- Compatibility layer between the V5.13 contract and V5.14 mock connector.
- Capability matrix.
- Safety guard.
- Report and CLI.
- API endpoints under `/api/v5/broker-adapter/*`.
- Frontend page at `/v5-broker-adapter`.

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
python scripts/run_v515_broker_adapter_skeleton.py --list
python scripts/run_v515_broker_adapter_skeleton.py --test ibkr_skeleton
python scripts/run_v515_broker_adapter_skeleton.py --test alpaca_skeleton
```

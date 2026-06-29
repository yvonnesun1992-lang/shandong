# V5.23 Provider Sandbox Connector Offline Replay Harness

V5.23 validates mock connector event sequencing with local placeholder replay events only.

It does not access a provider portal, create keys, connect to a broker, call a sandbox API, read accounts, read balances, read positions, submit orders, or touch real money.

## Scope

- Offline replay mode defaults to `offline_replay_only`.
- Replay runtime remains disabled.
- Sandbox API remains disabled.
- Account read remains disabled.
- Order submission remains disabled.
- Broker connected remains false.
- Real money remains disabled.
- Paper trading remains true.

## Replay Coverage

- `normal_order_lifecycle`
- `partial_fill_lifecycle`
- `rejected_order_lifecycle`
- `canceled_order_lifecycle`
- `timeout_then_recovery`
- `duplicate_order_replay`
- `rate_limit_then_backoff`
- `market_closed_rejection`
- `insufficient_funds_rejection`
- `state_machine_error_recovery`

## Safety Boundary

V5.23 does not return `provider_endpoint_url`. Offline events use placeholder identifiers only and store no raw provider payload.

V5.24 can add offline fault injection on top of this replay harness while keeping the same no-API boundary.

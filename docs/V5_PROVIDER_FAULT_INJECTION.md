# V5.24 Provider Sandbox Connector Fault Injection Suite

V5.24 validates selected provider mock connector fault handling with local placeholder fault events only.

It does not access a provider portal, create keys, connect to a broker, call a sandbox API, read accounts, read balances, read positions, submit orders, or touch real money.

## Scope

- Fault injection mode defaults to `fault_injection_only`.
- Fault injection runtime remains disabled.
- Sandbox API remains disabled.
- Account read remains disabled.
- Order submission remains disabled.
- Broker connected remains false.
- Real money remains disabled.
- Paper trading remains true.

## Fault Coverage

- `connector_timeout`
- `provider_reject`
- `duplicate_order`
- `stale_response`
- `out_of_order_event`
- `partial_fill_mismatch`
- `rate_limit_storm`
- `audit_loss`
- `state_machine_corruption`
- `recovery_rollback`
- `kill_switch_trigger`
- `idempotency_collision`

## Safety Boundary

V5.24 does not return `provider_endpoint_url`. Fault scenarios use placeholder identifiers only and store no raw provider payload.

V5.25 can add offline soak and stability gates after this fault suite is reviewed and merged.

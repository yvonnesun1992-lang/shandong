# V5.23 Provider Sandbox Connector Offline Replay Harness

Final verdict: PASS

Current phase is offline replay harness only.

Boundary:
- Offline replay mode: offline_replay_only
- Provider: alpaca
- Replay runtime enabled: false
- Sandbox API enabled: false
- Account read enabled: false
- Order submission enabled: false
- Broker connected: false
- Real money enabled: false
- Paper trading: true

Replay scenario catalog:
- normal_order_lifecycle, partial_fill_lifecycle, rejected_order_lifecycle, canceled_order_lifecycle, timeout_then_recovery, duplicate_order_replay, rate_limit_then_backoff, market_closed_rejection, insufficient_funds_rejection, state_machine_error_recovery

Replay runner results:
- Total scenarios: 10
- Passed: 10
- Failed: 0

Replay consistency validation:
- Valid: True
- Validated scenarios: 10

Failure recovery validation:
- Valid: True
- Recovery scenarios checked: timeout_then_recovery, rate_limit_then_backoff, duplicate_order_replay, state_machine_error_recovery

Audit trail validation:
- Audit event generated for every replay step.
- Raw payload stored: false
- Provider payload redacted: true

Safety validation:
- Safe: True
- No broker SDK import.
- No network calls.
- No plaintext credentials.
- No real account reference.
- No real order reference.
- No raw provider payload.
- No provider endpoint URL.

Missing production requirements:
- Real sandbox connector remains disabled.
- Sandbox API remains disabled.
- Account read remains disabled.
- Order submission remains disabled.
- Provider portal access remains disabled.
- Runtime validation remains future work.

This is not a production trading system.

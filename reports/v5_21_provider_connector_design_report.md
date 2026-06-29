# V5.21 Provider-Specific Sandbox Connector Design

Verdict: PASS

## Connector Design Mode

- Mode: design_only
- Design provider: alpaca
- Design only: true
- Connector runtime enabled: false
- Sandbox API enabled: false
- Account read enabled: false
- Order submission enabled: false
- Broker connected: false
- Real money enabled: false
- Paper trading: true

## Field Mapping Design

- Rows: 10
- Requires future provider docs: true

## Order Request Mapping

- Required internal fields: 14
- Order submission enabled: false

## Order Response Mapping

- Raw response policy: redacted_only

## Account / Position Mapping

- Real account read enabled: false
- Sandbox account read enabled: false

## Error Mapping Design

- Error types: 13

## Rate Limit Policy

- Network calls enabled: false

## Idempotency Policy

- Duplicate order protection: true

## Order State Machine Design

- States: 12
- Sandbox submission enabled: false
- Real submission enabled: false

## Connector Safety Boundary

- Safe: true
- Errors: 0

## Missing Production Requirements

- future provider docs must be reviewed by a human
- connector runtime remains disabled
- sandbox API remains disabled
- account read remains disabled
- order submission remains disabled
- credential vault remains future work

## Boundary

Current stage is provider-specific connector design only.
Current stage does not access provider portal.
Current stage does not connect to a real broker.
Current stage does not connect to sandbox API.
Current stage does not create API keys.
Current stage does not read real accounts.
Current stage does not submit real or sandbox orders.
Current stage does not use real funds.
Current stage is not a production trading system.

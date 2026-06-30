# V5.28 Pre-Sandbox Operator Approval Gate

V5.28 adds a design-only approval gate for future sandbox preparation. It does not connect to a broker, sandbox API, provider portal, credential vault, real account, or real funds.

## What It Shows

- Approval request schema placeholders
- Evidence requirements before sandbox preparation
- Operator role policy
- Risk acknowledgement policy
- Approval gate evaluation
- Approval audit trail design
- Safety validation

## Locked Boundaries

- Approval runtime disabled
- Operator approval cannot unlock sandbox access
- Sandbox API disabled
- Secret read disabled
- Broker connected false
- Order submission disabled
- Real money disabled
- Paper trading only

Even if `SHANDONG_V5_OPERATOR_APPROVAL_GRANTED=true` or related enablement variables are set, V5.28 only reports a warning and keeps every real path disabled.

## Not Included

- No real broker API
- No sandbox broker API
- No provider portal access
- No account creation
- No API key creation
- No secret read or storage
- No account read
- No order submission
- No raw provider payload
- No endpoint URL exposure
- No production trading

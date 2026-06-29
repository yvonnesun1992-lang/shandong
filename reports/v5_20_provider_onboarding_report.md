# V5.20 Selected Provider Sandbox Onboarding Runbook

Verdict: PASS

## Onboarding Mode

- Mode: runbook_only
- Runbook only: true
- Provider portal access enabled: false
- API key creation enabled: false
- Sandbox API enabled: false
- Broker connected: false
- Real orders enabled: false
- Real money enabled: false
- Paper trading: true

## Selected Provider

- Provider: alpaca
- Source: v519_report

## Account Opening Runbook

- Ready: false
- Steps: 10

## Sandbox Access Runbook

- Ready: false
- Steps: 10

## API Key Preparation Runbook

- Ready: false
- Credential storage: future_vault

## Market Data Onboarding Runbook

- Ready: false
- Steps: 11

## Approval and Risk Runbook

- Ready: false
- Manual approval required: true
- Kill switch required: true

## Sandbox Dry Run Runbook

- Ready: false
- Sandbox orders enabled: false

## Onboarding Safety Validation

- Safe: true
- Errors: 0

## Blocking Items

- human must review account type and jurisdiction requirements
- human must decide whether account opening is appropriate
- provider portal access remains disabled
- sandbox endpoint must remain unconfigured in V5.20
- sandbox connectivity cannot be tested in this phase
- sandbox order submission remains disabled
- future credential vault must be selected before any key exists
- API key creation remains disabled
- frontend exposure of credentials remains prohibited
- market data API access remains disabled
- exchange entitlements are not verified in V5.20
- commercial data usage requires future review
- manual approval gate must be enforced before sandbox connection
- kill switch must be tested before sandbox connection
- order preview must remain mandatory
- dry run cannot execute until a future connector design is approved
- sandbox orders remain disabled by default
- credential vault validation is only a future checklist item

## Boundary

Current stage is provider onboarding runbook only.
Current stage does not access provider portal.
Current stage does not connect to a real broker.
Current stage does not connect to sandbox API.
Current stage does not submit real or sandbox orders.
Current stage does not use real funds.
Current stage is not a production trading system.

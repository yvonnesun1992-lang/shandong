# V5.20 Selected Provider Sandbox Onboarding Runbook

V5.20 prepares an operator-facing runbook for the selected provider from V5.19. It is a planning and readiness artifact only.

## What It Includes

- Selected provider resolver using the local V5.19 report, config, or fallback provider.
- Account opening preparation checklist.
- Sandbox access preparation checklist.
- API key preparation checklist for a future credential vault.
- Market data onboarding checklist.
- Approval and risk checklist.
- Sandbox dry run checklist.
- Onboarding safety validation.
- CLI report and API endpoints.

## Safety Boundaries

- No provider portal access.
- No real broker connection.
- No sandbox API connection.
- No API key creation.
- No API key, secret, token, or password storage.
- No account reads.
- No real balance or position reads.
- No real or sandbox orders.
- No real money.
- No OAuth.
- No external network requests.
- No external log upload.
- No production trading.
- No alpha, factor, or strategy changes.

## API

- `GET /api/v5/provider-onboarding/status`
- `GET /api/v5/provider-onboarding/selected-provider`
- `GET /api/v5/provider-onboarding/account-opening`
- `GET /api/v5/provider-onboarding/sandbox-access`
- `GET /api/v5/provider-onboarding/api-key`
- `GET /api/v5/provider-onboarding/market-data`
- `GET /api/v5/provider-onboarding/approval-risk`
- `GET /api/v5/provider-onboarding/sandbox-dry-run`
- `GET /api/v5/provider-onboarding/safety`

Every response keeps `runbook_only=true`, `broker_connected=false`, `sandbox_api_enabled=false`, `real_orders_enabled=false`, `real_money_enabled=false`, and `paper_trading=true`.

## CLI

```bash
python scripts/run_v520_provider_onboarding.py
python scripts/run_v520_provider_onboarding.py --provider alpaca
python scripts/run_v520_provider_onboarding.py --provider ibkr
python scripts/run_v520_provider_onboarding.py --check safety
python scripts/run_v520_provider_onboarding.py --check dry-run
```

The CLI writes `reports/v5_20_provider_onboarding_report.md`.

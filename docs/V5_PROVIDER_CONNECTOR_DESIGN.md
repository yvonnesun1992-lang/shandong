# V5.21 Provider-Specific Sandbox Connector Design

V5.21 designs a provider-specific sandbox connector blueprint for the selected provider. It does not enable connector runtime.

## What It Includes

- Provider field mapping design.
- Order request mapping design.
- Order response mapping design.
- Account and position placeholder mapping.
- Provider error mapping design.
- Rate limit policy design.
- Idempotency policy design.
- Order state machine design.
- Connector safety boundary.
- CLI report and API endpoints.

## Safety Boundaries

- No provider portal access.
- No real broker connection.
- No sandbox API connection.
- No broker SDK imports.
- No API key creation.
- No API key, secret, token, or password storage.
- No account reads.
- No real balance or position reads.
- No real or sandbox orders.
- No raw provider payload storage.
- No provider endpoint URL.
- No external network requests.
- No external log upload.
- No production trading.
- No alpha, factor, or strategy changes.

## API

- `GET /api/v5/provider-connector-design/status`
- `GET /api/v5/provider-connector-design/field-mapping`
- `GET /api/v5/provider-connector-design/order-request`
- `GET /api/v5/provider-connector-design/order-response`
- `GET /api/v5/provider-connector-design/account-position`
- `GET /api/v5/provider-connector-design/error-mapping`
- `GET /api/v5/provider-connector-design/rate-limit`
- `GET /api/v5/provider-connector-design/idempotency`
- `GET /api/v5/provider-connector-design/state-machine`
- `GET /api/v5/provider-connector-design/safety`

Every response keeps `design_only=true`, `connector_runtime_enabled=false`, `sandbox_api_enabled=false`, `account_read_enabled=false`, `order_submission_enabled=false`, `broker_connected=false`, `real_money_enabled=false`, and `paper_trading=true`.

## CLI

```bash
python scripts/run_v521_provider_connector_design.py
python scripts/run_v521_provider_connector_design.py --provider alpaca
python scripts/run_v521_provider_connector_design.py --provider ibkr
python scripts/run_v521_provider_connector_design.py --check safety
python scripts/run_v521_provider_connector_design.py --check state-machine
```

The CLI writes `reports/v5_21_provider_connector_design_report.md`.

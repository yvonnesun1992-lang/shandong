# V5.22 Provider Sandbox Connector Mock Contract Test

V5.22 validates the V5.21 provider connector design with local mock payloads only. It does not run a connector.

## What It Includes

- Mock provider payload catalog.
- Contract schema validator.
- Request mapping contract test.
- Response normalization contract test.
- Error mapping contract test.
- Idempotency contract test.
- Order state machine contract test.
- Mock contract safety validation.
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

- `GET /api/v5/provider-mock-contract/status`
- `GET /api/v5/provider-mock-contract/payloads`
- `GET /api/v5/provider-mock-contract/schema-validation`
- `GET /api/v5/provider-mock-contract/request-mapping`
- `GET /api/v5/provider-mock-contract/response-normalization`
- `GET /api/v5/provider-mock-contract/error-mapping`
- `GET /api/v5/provider-mock-contract/idempotency`
- `GET /api/v5/provider-mock-contract/state-machine`
- `GET /api/v5/provider-mock-contract/safety`
- `GET /api/v5/provider-mock-contract/summary`

Every response keeps `mock_contract_only=true`, `mock_contract_runtime_enabled=false`, `sandbox_api_enabled=false`, `account_read_enabled=false`, `order_submission_enabled=false`, `broker_connected=false`, `real_money_enabled=false`, and `paper_trading=true`.

## CLI

```bash
python scripts/run_v522_provider_mock_contract.py
python scripts/run_v522_provider_mock_contract.py --provider alpaca
python scripts/run_v522_provider_mock_contract.py --provider ibkr
python scripts/run_v522_provider_mock_contract.py --check safety
python scripts/run_v522_provider_mock_contract.py --check schema
python scripts/run_v522_provider_mock_contract.py --check state-machine
```

The CLI writes `reports/v5_22_provider_mock_contract_report.md`.

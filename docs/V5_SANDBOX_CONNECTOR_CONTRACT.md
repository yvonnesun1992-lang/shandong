# V5.13 Sandbox Connector Contract Planning

V5.13 defines the contract for a future broker sandbox connector. It does not
implement a real connector, import a broker SDK, connect to a sandbox API, read
credentials, submit orders, or access real capital.

## Goal

The goal is to document and test the interface boundary before any external
connector runtime exists:

- connector interface contract
- request schema
- response schema
- error code contract
- idempotency policy
- rate limit policy
- retry policy
- credential boundary contract
- connector safety validator
- API, report, CLI, and frontend page

## Why Contract Planning First

Broker sandbox runtimes require credentials, provider-specific order fields,
rate limits, retry behavior, and safety gates. V5.13 keeps runtime disabled and
defines the shape future implementations must satisfy.

## Contract Sections

- `connector_interface_contract.py`: required future connector methods
- `request_schema_contract.py`: submit, cancel, and status request schemas
- `response_schema_contract.py`: sanitized order, account, and position responses
- `error_code_contract.py`: normalized connector error codes
- `idempotency_policy.py`: stable duplicate detection planning
- `rate_limit_policy.py`: local rate limit policy
- `retry_policy.py`: retryable and non-retryable error planning
- `credential_boundary_contract.py`: future credential injection boundary
- `connector_safety_validator.py`: no-runtime and no-real-order safety checks

## CLI

```bash
python scripts/run_v513_sandbox_connector_contract.py
```

The CLI writes `reports/v5_13_sandbox_connector_contract_report.md`.

## API Endpoints

- `GET /api/v5/sandbox-connector/status`
- `GET /api/v5/sandbox-connector/interface-contract`
- `GET /api/v5/sandbox-connector/request-schema`
- `GET /api/v5/sandbox-connector/response-schema`
- `GET /api/v5/sandbox-connector/error-codes`
- `GET /api/v5/sandbox-connector/idempotency`
- `GET /api/v5/sandbox-connector/rate-limit`
- `GET /api/v5/sandbox-connector/retry-policy`
- `GET /api/v5/sandbox-connector/credential-boundary`
- `GET /api/v5/sandbox-connector/readiness`

## Frontend Page

`web/frontend/app/v5-sandbox-connector/page.tsx` shows contract status,
safety boundary, interface contract, request schema, response schema, error
codes, idempotency, rate limit, retry policy, credential boundary, and final
verdict.

## Safety Boundary

- Connector runtime is disabled.
- Sandbox API connection is disabled.
- Real broker connection is disabled.
- Real order submission is disabled.
- Real capital movement is disabled.
- Production live trading is disabled.
- Alpha model, factor logic, and strategy logic are unchanged.

## Known Limitations

This is contract planning only. It does not validate provider SDK behavior,
broker-side rejects, real rate limits, or real network behavior.

## Next Step

The next safe step is a sandbox connector mock implementation that still does
not connect to an external broker and still keeps credential handling behind a
future vault boundary.

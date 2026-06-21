# Local Demo Guide

## How to run local backend

Run the verification chain first:

```bash
python scripts/startup_check.py
python scripts/v2_integration_check.py
python scripts/local_startup_verification.py
```

The FastAPI application supports a local uvicorn launch:

```bash
python -m uvicorn src.api.v2.server:create_v2_api_app --factory --reload
```

If `uvicorn` is not installed in the local environment, use the verification scripts and FastAPI `TestClient` tests as the local startup proof.

## Key API endpoints

- `/api/v2/health`
- `/api/v2/system/liveness`
- `/api/v2/system/readiness`
- `/api/v2/system/security-health`
- `/api/v2/system/db-health`
- `/api/v2/system/workspace-health`
- `/api/v2/system/billing-health`
- `/api/v2/admin/console`
- `/api/v2/auth/login`
- `/api/v2/auth/me`

## How to run frontend

The Next.js frontend shell lives in:

```bash
cd web/frontend
node scripts/verify-build.mjs
```

The current repository includes a structure verification script for frontend demo readiness. If `npm` or `pnpm` is unavailable or blocked by local dependency build approval, this script is the supported lightweight frontend check.

## Demo script

1. Run `python scripts/startup_check.py`.
2. Run `python scripts/v2_integration_check.py`.
3. Run `python scripts/local_startup_verification.py`.
4. Run `python scripts/deployment_dry_run_check.py`.
5. Run `python scripts/v3_release_candidate_check.py`.
6. Start the API with `python -m uvicorn src.api.v2.server:create_v2_api_app --factory --reload` if uvicorn is available.
7. Open or describe the Admin Console at `/api/v2/admin/console` and the frontend page at `web/frontend/app/admin/page.tsx`.
8. Explain safety boundaries: no broker connection, no automatic trading, no real payment execution, no external AI calls, and no production secrets.

## V3.6 Product Demo Freeze

V3.6 freezes the product demo candidate. It is still demo / dry run only, not a production launch, and it cannot be used for real trading or real customer funds.

Run:

```bash
python scripts/v3_release_candidate_check.py
```

## Demo talking points

- V2.0 to V2.8 created the production foundation layers.
- V2.9 verifies that those layers can start locally and are documented for review.
- V3.0 to V3.6 polish and freeze the product demo flow.
- The Admin Console summarizes platform readiness without exposing credentials or local paths.
- Mock auth and mock billing are intentionally documented limitations.

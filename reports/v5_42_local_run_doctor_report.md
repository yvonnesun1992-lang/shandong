# V5.42 Local Run Doctor Report

- command availability: python=True, node=False, pnpm=True
- port diagnosis: frontend_3000=False, backend_8000=False
- backend diagnosis: ready=True
- frontend diagnosis: ready=True
- browser targets: localhost only
- likely reason 3000 not open: Node.js is not available, so frontend cannot start

## Recommended Next Steps

- Install Node.js LTS, then reopen your terminal.
- Run cd web/frontend && pnpm install.
- Run cd web/frontend && pnpm dev --hostname 127.0.0.1 --port 3000.
- Run python -m uvicorn src.api.v2.server:create_v2_api_app --factory --host 127.0.0.1 --port 8000.
- Open http://127.0.0.1:3000 after both local servers are running.

## Mac Fix Guide

- Mac fix guide
- 1. Install Node.js LTS if Node is missing.
- 2. Reopen Terminal after installing Node.js.
- 3. Go to the shandong project folder.
- 4. Run python scripts/run_v541_local_e2e_verification.py.
- 5. Run python scripts/run_v539_local_launcher.py --run.
- 6. Open http://127.0.0.1:3000.

## Windows Fix Guide

- Windows fix guide
- 1. Install Node.js LTS if Node is missing.
- 2. Reopen PowerShell after installing Node.js.
- 3. Go to the shandong project folder.
- 4. Run python scripts/run_v541_local_e2e_verification.py.
- 5. Run python scripts/run_v539_local_launcher.py --run.
- 6. Open http://127.0.0.1:3000.

## Safety Boundary

- Current stage is local run doctor only.
- It does not automatically install dependencies.
- It does not connect to a real broker.
- It does not connect to a sandbox API.
- It does not read secrets.
- It does not read accounts, balances, or positions.
- It does not submit orders.
- It does not connect to real money.

## Missing Local Requirements

- Start commands remain manual copy/paste steps.
- Browser opening remains a local user action.

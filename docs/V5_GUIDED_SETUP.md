# V5.43 Guided Local Setup Wizard

V5.43 adds a guided local setup wizard for users who cannot open `http://127.0.0.1:3000`.

## What It Explains

- `3000` is the frontend browser page.
- `8000` is the backend API service.
- Node.js is needed to run the web frontend.
- pnpm is needed to install and run frontend dependencies.
- Backend TestClient success means backend code is valid, but it does not mean the browser page has started.
- If `127.0.0.1:3000` does not open, the frontend is usually not running.

## What It Provides

- Missing requirements.
- Mac setup steps.
- Windows setup steps.
- Copy command blocks.
- Plain language explanation.
- Recommended next step.
- Safety boundary summary.

## Safety Boundary

- Current stage is guided setup wizard only.
- It does not automatically install dependencies.
- It does not automatically access external networks.
- It does not modify PATH.
- It does not request administrator permissions.
- It does not start long-running services.
- It does not connect to brokers.
- It does not connect to sandbox APIs.
- It does not read secrets.
- It does not read accounts, balances, or positions.
- It does not submit orders.
- It does not use real money.

## How To Run

```bash
python scripts/run_v543_guided_setup_wizard.py
python scripts/run_v543_guided_setup_wizard.py --check requirements
python scripts/run_v543_guided_setup_wizard.py --check steps
python scripts/run_v543_guided_setup_wizard.py --check commands
python scripts/run_v543_guided_setup_wizard.py --check explain
```

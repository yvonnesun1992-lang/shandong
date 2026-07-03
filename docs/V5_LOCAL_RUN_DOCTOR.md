# V5.42 Local Run Doctor

V5.42 adds a local run diagnosis layer for users who cannot open `http://127.0.0.1:3000`.

## Scope

- Command availability checks for Python, Node, npm, and pnpm.
- Localhost-only port checks for `127.0.0.1:3000` and `127.0.0.1:8000`.
- Backend TestClient smoke checks.
- Frontend file and dependency-state checks.
- Browser target validation for localhost URLs only.
- Human-friendly Mac and Windows fix guides.
- Local run doctor report generation.

## Safety Boundary

- Current stage is local run doctor only.
- It does not automatically install dependencies.
- It does not start long-running services.
- It does not connect to brokers.
- It does not connect to sandbox APIs.
- It does not read secrets.
- It does not read accounts, balances, or positions.
- It does not submit orders.
- It does not use real money.

## How To Run

```bash
python scripts/run_v542_local_run_doctor.py
python scripts/run_v542_local_run_doctor.py --check commands
python scripts/run_v542_local_run_doctor.py --check ports
python scripts/run_v542_local_run_doctor.py --check backend
python scripts/run_v542_local_run_doctor.py --check frontend
python scripts/run_v542_local_run_doctor.py --check fix-guide
```

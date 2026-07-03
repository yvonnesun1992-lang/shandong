# V5.39 Local Desktop Launcher Report

- launcher mode: local_launcher_only
- verdict: WARNING
- environment ready: True
- port check ready: True
- backend command: `python -m uvicorn src.api.v2.server:create_v2_api_app --factory --host 127.0.0.1 --port 8000`
- frontend command: `cd web/frontend && pnpm dev --hostname 127.0.0.1 --port 3000`
- browser target: `http://127.0.0.1:3000`
- Mac users: double click `scripts/start_shandong_mac.command`.
- Windows users: double click `scripts/start_shandong_windows.bat`.

## Safety Boundary

- Current package is a local launcher only.
- It is not a formal Mac .app installer.
- It is not a Windows .exe installer.
- It does not connect to a real broker.
- It does not connect to a sandbox API.
- It does not read secrets.
- It does not read accounts, balances, or positions.
- It does not submit orders.
- It does not connect to real money.

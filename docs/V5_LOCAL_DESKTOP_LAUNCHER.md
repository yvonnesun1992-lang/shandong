# V5.39 Local Desktop Launcher

V5.39 adds a local desktop launcher layer for starting the Shandong platform from a user machine.

The launcher checks the local environment, prepares backend and frontend startup commands, checks localhost ports, opens the local browser target, writes startup logs, and provides Mac / Windows helper scripts.

## Usage

```bash
python scripts/run_v539_local_launcher.py --dry-run
python scripts/run_v539_local_launcher.py --check environment
python scripts/run_v539_local_launcher.py --check ports
python scripts/run_v539_local_launcher.py --check safety
```

Mac users can double click:

```text
scripts/start_shandong_mac.command
```

Windows users can double click:

```text
scripts/start_shandong_windows.bat
```

## Localhost Boundary

- Backend target: `http://127.0.0.1:8000`
- Frontend target: `http://127.0.0.1:3000`
- Browser target: `http://127.0.0.1:3000`
- External hosts are blocked and replaced with localhost.

## What V5.39 Is Not

- Not a formal Mac `.app` installer.
- Not a Windows `.exe` installer.
- Not a broker connector.
- Not a sandbox API client.
- Not a credential reader.
- Not an account, balance, or position reader.
- Not an order preview or order submission system.

## Safety Boundary

V5.39 remains paper trading only. It does not connect to a broker, does not connect to a sandbox API, does not read secrets, does not read accounts, does not read balances or positions, does not submit orders, and does not connect to real money.

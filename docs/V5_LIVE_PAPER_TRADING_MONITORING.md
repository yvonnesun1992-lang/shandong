# V5.4 Live Paper Trading Monitoring API

V5.4 adds a dashboard-ready monitoring layer for the V5 paper trading runtime. It reads local runtime logs, checkpoints, and the V5.3 soak report, then exposes safe API responses and a frontend page.

## Goal

Trading Engine / Runtime Logs / Checkpoints / Soak Reports -> Monitoring Data Layer -> API Endpoints -> Dashboard-ready JSON -> Health / Risk / PnL Visibility

## Monitoring API Endpoints

- `GET /api/v5/monitoring/summary`
- `GET /api/v5/monitoring/pnl`
- `GET /api/v5/monitoring/positions`
- `GET /api/v5/monitoring/signals`
- `GET /api/v5/monitoring/trades`
- `GET /api/v5/monitoring/errors`
- `GET /api/v5/monitoring/health`
- `GET /api/v5/monitoring/risk`
- `GET /api/v5/monitoring/soak-report`

All endpoints return paper trading safety flags:

- `paper_trading: true`
- `real_trading: false`
- `broker_connected: false`

## Dashboard Page

The frontend page lives at:

```text
web/frontend/app/v5-monitoring/page.tsx
```

It shows system status, paper-trading safety boundaries, PnL, positions, signals, trades, risk, health, errors, and the soak test report summary. The page uses safe fallback data if the backend is unavailable.

## Monitoring Snapshot CLI

Run:

```bash
python scripts/run_v54_monitoring_snapshot.py
```

The command prints a JSON summary and writes:

```text
reports/v5_4_monitoring_report.md
```

Exit code is `0` for `PASS` or `WARNING`, and non-zero for `FAIL`.

## Safety Boundary

- Paper trading only.
- Not real trading.
- No real broker connection.
- No real account.
- No real capital.
- No payment system.
- No production deployment.
- No external log upload.
- No external database dependency.
- No external AI API.
- No stored secret, token, password, authorization header, or API key.

## Known Limitations

- Monitoring is local-file based.
- It does not stream to an external observability vendor.
- It does not require the runtime to be active.
- It is a dashboard-ready monitoring layer, not a broker execution system.

## Next Step

The next safe step is a production deployment dry run with paper trading only, using local-safe secrets policy and no broker connectivity.

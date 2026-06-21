# Operations Runbook

## Start

```bash
docker compose up --build
```

## Stop

```bash
docker compose down
```

## Logs

```bash
docker compose logs -f api
docker compose logs -f ui
```

## Tests

```bash
python -m pytest
```

## Startup Check

```bash
python scripts/startup_check.py
```

## Deployment Dry Run

V3.5 adds an external deployment dry run. It is a rehearsal only, not a production launch.

```bash
python scripts/deployment_dry_run_check.py
```

The check should report `success: true` before moving to any later deployment planning. If it fails, inspect the named check, fix local configuration or missing docs, and rerun it. Do not add real cloud credentials, real database endpoints, real domain configuration, or TLS material to the repo.

## Health Endpoints

```bash
curl http://localhost:8000/api/v2/system/liveness
curl http://localhost:8000/api/v2/system/readiness
curl http://localhost:8000/api/v2/system/deployment-dry-run
```

## Database Warning

Check that the database parent directory exists, that the SQLite path is writable, and that migrations can run.

## Key Rotation Concept

API keys and sessions are stored hashed. Rotate by revoking old records, issuing new values, and asking clients to update their local configuration.

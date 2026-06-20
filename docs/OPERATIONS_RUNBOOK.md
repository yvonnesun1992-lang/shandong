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

## Health Endpoints

```bash
curl http://localhost:8000/api/v2/system/liveness
curl http://localhost:8000/api/v2/system/readiness
```

## Database Warning

Check that the database parent directory exists, that the SQLite path is writable, and that migrations can run.

## Key Rotation Concept

API keys and sessions are stored hashed. Rotate by revoking old records, issuing new values, and asking clients to update their local configuration.

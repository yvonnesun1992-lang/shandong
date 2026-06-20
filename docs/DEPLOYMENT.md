# Deployment Guide

V2.6 provides a production-like operations package for the research SaaS foundation.

## Local Development

1. Copy `.env.example` to `.env` for local-only use.
2. Keep `SHANDONG_AUTH_MODE=local` for local development.
3. Run `python scripts/startup_check.py`.
4. Start API with `python -m uvicorn src.api.v2.server:app --reload`.
5. Start UI with `streamlit run app/main.py`.

## Production-like Compose

Use `docker-compose.prod.example.yml` as a template. It references `.env`, but real `.env` files must not be committed.

## Environment Variables

Production operators should set secure values outside git, use production auth mode, require auth, and disable local admin fallback.

## Startup Check

Run:

```bash
python scripts/startup_check.py
```

## Health Checks

- Liveness: `/api/v2/system/liveness`
- Readiness: `/api/v2/system/readiness`
- Database: `/api/v2/system/db-health`

## Rollback

Rollback to a stable tag with normal git deployment procedures, for example `v1.34-stable` or a newer approved release tag.

## Database Backup

For SQLite, back up `data/shandong_v2.db` while the service is stopped or through a filesystem snapshot. PostgreSQL remains configuration-ready but is not required locally.

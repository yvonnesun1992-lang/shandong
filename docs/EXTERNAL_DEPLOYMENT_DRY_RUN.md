# External Deployment Dry Run

## Current State

- local backend
- local frontend shell
- Dockerfile exists
- docker-compose examples exist
- no production cloud connected
- no production database connected
- no production secret configured

## Dry Run Goals

- verify backend startup
- verify frontend structure
- verify API health endpoints
- verify Admin Console readiness
- verify observability endpoint
- verify identity plan endpoint
- verify no secrets committed

## Deployment Targets Planned

- local Docker
- Render planned
- Railway planned
- Fly.io planned
- Vercel frontend planned
- Cloud PostgreSQL planned

## Required Future Decisions

- hosting provider
- database provider
- identity provider
- secrets manager
- domain
- TLS
- logging / monitoring
- backup and recovery
- rollback strategy

## Not Implemented Yet

- No production deployment
- No cloud provider connected
- No production database connected
- No production secret configured
- No real domain
- No TLS certificate
- No external logs
- No real payment
- No broker connection
- No auto trading

## V3.6 Release Candidate Freeze

V3.6 adds release candidate QA for the product demo. Run:

```bash
python scripts/v3_release_candidate_check.py
```

This is not a production launch. The system remains demo / dry run only and cannot be used for real trading or real customer funds.

# Production Deployment Target Selection

## Current State

- current deployment is local/demo
- no production cloud connected
- no real domain
- no TLS certificate
- no production database connected
- no production secret configured

## Candidate Targets

### Frontend

- Vercel planned
- Netlify planned
- Cloudflare Pages planned

### Backend

- Render planned
- Fly.io planned
- Railway planned
- AWS ECS planned
- GCP Cloud Run planned

### Database

- PostgreSQL planned
- Neon planned
- Supabase Postgres planned
- RDS planned

### Secrets

- platform managed secrets planned
- cloud secrets manager planned

### Monitoring

- Sentry planned
- OpenTelemetry planned
- cloud logs planned

## Recommended First Deployment Stack

- Frontend: Vercel planned
- Backend: Render or Fly.io planned
- Database: managed PostgreSQL planned
- Secrets: platform secrets planned
- Monitoring: Sentry / OpenTelemetry planned

## Decision Criteria

- cost
- simplicity
- Python backend support
- frontend hosting quality
- database reliability
- secrets support
- logs / monitoring support
- rollback support
- China access considerations if relevant

## Not Implemented Yet

- No production deployment
- No cloud provider connected
- No production token
- No DATABASE_URL
- No domain
- No TLS
- No external log upload
- No real payment
- No broker connection
- No auto trading

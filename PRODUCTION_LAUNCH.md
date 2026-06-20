# V1.34 Production Launch Architecture

## SaaS Architecture

V1.34 adds a production launch architecture layer for the Shandong SaaS platform. It includes a Next.js frontend structure, JWT session service, Stripe-compatible billing structure, Docker/Nginx deployment files, CI/CD verification, and monitoring primitives.

This version is deployment architecture only. It does not add trading execution, brokerage connectivity, price prediction, or AI investment advice.

## Frontend System

The frontend lives in `web/frontend/` and follows a Next.js app-router structure:

- login
- dashboard
- strategy
- reports
- risk
- settings
- api-docs

The UI uses a responsive enterprise shell, card layout, and a chart card component.

## Auth System

`src/auth/jwt_auth.py` provides:

- signup
- login
- JWT creation
- session validation
- protected route checks through RBAC

The implementation is local and structure-focused. It does not store sensitive user data.

## Billing System

`src/billing/stripe/` provides a Stripe-compatible billing shell:

- subscription structure
- checkout flow structure
- webhook handler structure
- plan catalog for free, pro, and team

All payment flows are mock-only and use `live_payment = False`.

## Deployment Guide

Production deployment files include:

- `deploy/Dockerfile.production`
- `deploy/docker-compose.production.yml`
- `deploy/nginx/nginx.conf`
- `.github/workflows/production-launch.yml`

The production compose file defines API, UI, and Nginx reverse proxy services.

## Monitoring

`src/monitoring/` provides:

- API latency tracking
- structured logs
- system health snapshot
- usage metrics

These primitives are local and can be connected to a managed observability stack later.

## Security Model

V1.34 keeps these boundaries:

- No broker connection.
- No automatic trading.
- No generated real trade instruction.
- No real trading logic.
- No stock price prediction.
- No AI API calls.
- No sensitive data persistence.
- No real payment processing.
- No core strategy logic changes.

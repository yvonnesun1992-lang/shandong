# Admin Console

The Admin Console is the V2.8 product control center for the Shandong SaaS research platform. It gives operators one place to review product and deployment status without changing strategy logic or adding trading behavior.

## What It Shows

- System Overview
- API Health
- Database Status
- Auth Mode
- Workspace Status
- Plan and Quota Status
- Deployment Readiness
- Release Candidate Status

## API Access

The aggregated endpoint is:

```text
GET /api/v2/admin/console
```

Local development mode can use the default admin fallback. Dev and production-style modes require an authenticated user with `admin:read` permission.

## UI Access

The Next.js product shell includes:

```text
web/frontend/app/admin/page.tsx
```

The page is intentionally simple: card layout, OK / Warning / Error badges, and no complex animation or new UI library dependency.

## Information Not Shown

The Admin Console must not display:

- Secrets
- Tokens
- Raw API keys
- Session identifiers
- Authorization headers
- Local absolute paths
- Database file paths
- `.env` contents

## Safety Boundaries

- No broker connection
- No automatic trading
- No real payment execution
- No live Stripe calls
- No external AI calls
- No production credential storage
- No core strategy logic changes

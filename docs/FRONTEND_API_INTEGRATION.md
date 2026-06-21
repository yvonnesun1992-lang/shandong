# V3.1 Frontend API Integration

## Goal

V3.1 connects the Next.js product shell to the FastAPI backend for safer, more realistic demos. The focus is Admin Console and Dashboard system status data.

## API Base URL

The frontend API client defaults to:

```text
http://localhost:8000
```

Override it with:

```text
NEXT_PUBLIC_API_BASE_URL
```

## Admin Console Data Source

Admin Console reads:

```text
/api/v2/admin/console
```

If the backend is unavailable, the page uses fallback demo data and displays a user-friendly error state.

## Dashboard Data Sources

Dashboard reads:

```text
/api/v2/system/liveness
/api/v2/system/readiness
/api/v2/system/security-health
/api/v2/system/workspace-health
/api/v2/system/billing-health
```

If one or more requests fail, the page keeps rendering with safe fallback content.

## Fallback Demo Data

Fallback data is intentionally static and safe. It exists so a local demo remains readable even when the API server is not running.

## Safety Sanitization

Frontend display data passes through sanitization before rendering. The sanitizer removes private fields, local absolute paths, and database filenames from text and payloads.

## Current Limits

- This is frontend API integration, not a trading feature.
- No broker connection.
- No auto trading.
- No real payment execution.
- No live Stripe calls.
- No external AI calls.
- No production credential storage.
- The frontend does not display private values, API credentials, or local machine paths.

# Observability Plan

## Current State

- Local observability only.
- API metrics are internal summary only.
- Health timeline is internal summary only.
- No external monitoring provider connected.
- No logs uploaded externally.

## What Is Collected

- Endpoint path.
- Status.
- Latency bucket / latency_ms.
- warning_count.
- Health snapshot status.
- error_count.

## What Is Not Collected

- no raw request body
- no password
- no token
- no session_id
- no authorization header
- no API key
- no local absolute path
- no production secret

## Future Options

These options are listed for future planning only:

- Prometheus
- Grafana
- Sentry
- Datadog
- OpenTelemetry
- Cloud logs

## Recommended Future Architecture

- Keep sensitive data redacted at source.
- Store metrics separately from raw logs.
- Use internal user_id only after production identity is ready.
- Add audit log retention policy later.
- Add error budget / SLO later.
- Add dashboard later.

## Not Implemented Yet

- No Sentry.
- No Datadog.
- No Grafana Cloud.
- No Prometheus remote write.
- No external log upload.
- No production monitoring key.

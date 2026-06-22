# V3 Product Demo Freeze

## V3 Release Candidate Scope

V3.0-V3.5 are frozen as a product demo release candidate:

- UI / UX polish
- Frontend API integration
- Demo auth / session UX
- Production identity planning
- Observability planning
- External deployment dry run

## Demo Flow

1. Run `python scripts/startup_check.py`.
2. Run `python scripts/v2_integration_check.py`.
3. Run `python scripts/local_startup_verification.py`.
4. Run `python scripts/deployment_dry_run_check.py`.
5. Run `python scripts/v3_release_candidate_check.py`.
6. Open Dashboard.
7. Open Login.
8. Login as Admin demo role.
9. Open Admin Console.
10. Explain identity / observability / deployment dry run modules.
11. Explain safety boundaries.

## Demo Safety Boundaries

- Research mode only.
- No broker connection.
- No auto trading.
- No real payment.
- No Stripe live API.
- No real identity provider.
- No OAuth.
- No production cloud connected.
- No external log upload.
- No AI API.
- No plaintext production secret.

## Known Limitations

- Demo auth is not production identity.
- Admin Console still uses safe fallback where backend is unavailable.
- Observability is local/internal only.
- Deployment is dry run only.
- Billing remains mock.
- No real cloud deployment.
- No real PostgreSQL production database.
- No production secrets manager.
- Frontend build may still depend on local npm/pnpm availability.

## Release Candidate Checklist

- Backend checks: startup, V2 integration, local startup, V3 release candidate.
- Frontend structure checks: dashboard, login, admin, API docs, shell components.
- Docs checks: UI/UX review, API integration, auth flow, identity plan, observability plan, external deployment dry run.
- Security boundary checks: no broker, no auto trading, no real payment, no external AI, no production identity, no external logs.
- Demo readiness checks: Admin Console modules, dashboard availability, demo auth UX, safe fallback states.

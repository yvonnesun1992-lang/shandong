# V5.18 Sandbox to Real Broker Transition Blueprint

V5.18 is a transition blueprint only. It documents the future path from local paper simulation and mock connector layers toward a possible broker sandbox review stage.

## Scope

- Defines transition status, readiness sections, environment separation, feature flags, sandbox enablement checklist, blocker policy, kill switch plan, rollback plan, and safety validation.
- Adds API endpoints under `/api/v5/transition/*`.
- Adds a frontend page at `/v5-transition`.
- Adds a CLI report generator at `scripts/run_v518_transition_blueprint.py`.

## Boundaries

- No real broker connection.
- No broker sandbox API connection.
- No account reads.
- No order submission.
- No real funds.
- No credential storage.
- No OAuth.
- No external network requests.
- No alpha model, factor logic, or strategy changes.

## Future Requirements

- Future credential vault with rotation and masking.
- Explicit environment separation for local, test, staging, sandbox, and production.
- Manual approval enforcement before any future sandbox stage.
- Kill switch rehearsal and rollback runbook approval.
- Legal, compliance, and operator review.

## Current Verdict

V5.18 keeps the system in paper trading mode and marks all real transition readiness as not ready.

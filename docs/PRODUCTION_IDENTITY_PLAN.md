# Production Identity Plan

## Current State

- Current auth is demo/mock.
- Demo session is local/demo only.
- No real production identity provider.
- No OAuth.
- No password storage.
- No external provider secret.

## Why Production Identity Needs Planning

Production identity cannot be attached casually because it affects security, session lifecycle, user lifecycle, workspace membership, billing ownership, audit log records, and compliance expectations.

## Future Options

These options are listed for future architecture planning only:

- OIDC provider
- Auth0
- Clerk
- Supabase Auth
- Firebase Auth
- Enterprise SSO
- Email magic link

## Recommended Future Architecture

- Keep backend AuthContext as the internal source of permission.
- External identity only verifies user identity.
- Backend maps external identity to internal user_id.
- Workspace membership remains internal.
- Quota / billing remains workspace-scoped.
- Audit log records internal user_id, not raw external token.

## Not Implemented Yet

- No OAuth implemented.
- No Google Login.
- No GitHub Login.
- No SMS login.
- No email magic link.
- No production password auth.
- No real provider secret.
- No production identity provider enabled.

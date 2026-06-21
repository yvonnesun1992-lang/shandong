# V3.2 Frontend Auth Flow

## Goal

V3.2 adds a product-friendly demo auth and session experience to the frontend. It is designed for local demos and role-aware UI flows.

## What Demo Login Means

Demo login calls the existing backend mock login endpoint and stores a local demo session in browser storage. This is useful for demonstrating Admin, User, and Viewer roles without adding a real identity service.

## Why This Is Not Production Auth

The demo session is stored in `localStorage`, which is acceptable for local demos but not suitable for a production identity system. Production auth planning belongs in a later V3.3 layer.

## Roles

- Admin: can review Admin Console flows.
- User: can access normal research workflows with limited admin controls.
- Viewer: can inspect read-oriented product views.

## Admin Console Permissions

Admin Console displays auth state at the top of the page. If a role does not have access, the UI shows a permission notice instead of a stack trace or private data.

## Dashboard Auth Status

Dashboard displays the current demo role and whether a demo session is active. Health widgets still fall back safely if the API or session is unavailable.

## Current Limits

- No real identity provider.
- No OAuth.
- No Google Login.
- No GitHub Login.
- No SMS verification.
- No stored password.
- No stored API key.
- No production credential storage.
- No broker connection.
- No automatic trading.
- No real payment execution.
- No live Stripe calls.
- No external AI calls.

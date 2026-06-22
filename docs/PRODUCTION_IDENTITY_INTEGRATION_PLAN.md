# Production Identity Integration Plan

## Current State

- current auth is demo/local
- no production identity provider connected
- no OAuth connected
- no Google/GitHub login
- no production session lifecycle
- no external identity mapping

## Why Identity Integration Matters

- real users
- workspace ownership
- billing ownership
- audit logs
- support / account recovery
- security
- compliance

## Recommended Future Architecture

- external provider verifies identity
- backend creates internal user_id
- backend maps user_id to workspace membership
- permission service remains internal
- quota/billing remain workspace-scoped
- audit log records internal user_id
- never store raw external token in logs
- use secrets manager for provider keys

## Identity Mapping Checklist

- external subject
- email
- internal user_id
- workspace membership
- role mapping
- account recovery
- user deletion / offboarding

## Session Lifecycle Checklist

- login
- refresh
- expiry
- logout
- revocation
- compromised session handling
- audit log
- support override policy

## Not Implemented Yet

- No production identity provider connected
- No OAuth implemented
- No Google Login
- No GitHub Login
- No SMS login
- No email magic link
- No client_id
- No client_secret
- No access token
- No refresh token
- No production session lifecycle

## Safety Boundaries

- no broker connection
- no auto trading
- no real payment execution
- no external AI API calls
- no production launch
- no real identity provider connected

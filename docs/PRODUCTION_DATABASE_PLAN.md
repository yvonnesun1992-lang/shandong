# Production Database Plan

## Current State

- current database is local/demo
- SQLite is suitable for local demo
- no production PostgreSQL connected
- no DATABASE_URL committed
- no production database credentials

## Why Production Database Needs Planning

- data durability
- multi-tenant isolation
- backup and recovery
- migration safety
- audit logs
- usage / billing / workspace data
- rollback policy

## Recommended Future Architecture

- PostgreSQL as production database
- secrets manager for connection string
- staging database before production
- migration dry run
- automated backup
- restore test
- read-only reporting replica later

## Migration Checklist

- choose provider
- create staging database
- configure secrets manager
- run migrations in staging
- run tests
- backup before migration
- rollback plan
- production cutover

## Not Implemented Yet

- No production database connected
- No PostgreSQL connection enabled
- No production DATABASE_URL
- No database password
- No real customer data migration
- No production backup policy
- No production restore test

## Safety Boundaries

- no broker connection
- no auto trading
- no real payment execution
- no external AI API calls
- no production launch
- no real customer data migration

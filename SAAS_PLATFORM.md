# V1.33 SaaS Platform

## SaaS 架构说明

V1.33 adds a full SaaS product architecture shell on top of the V1.32 release layer. It includes mock user sessions, RBAC permissions, local API key management, static web page structure, and simulated billing plans.

This is a product architecture foundation, not a real authentication, payment, or trading system.

## 用户系统

`src/auth/` provides:

- `User`
- `SessionManager`
- `login()`
- `logout()`
- user context and account context helpers

The login flow is mock-only and stores session state in memory for local demos and tests.

## API 体系

`src/auth/api_keys.py` provides a local API key manager:

- generate key
- revoke key
- simple rate limit
- basic usage tracking

Keys are mock local values for architecture testing. They are not external service credentials.

## 权限体系

`src/core/rbac.py` defines three roles:

- admin
- user
- viewer

Resources covered:

- report
- dashboard
- api

The RBAC layer exposes `can_access()` and `require_permission()` for product-level access checks.

## Web 前端结构

`web/` includes static product page shells:

- login
- dashboard
- strategy center
- report viewer
- trend page
- API docs

These pages are static structure only and do not implement real sign-in.

## 计费结构

`src/billing/` provides simulated SaaS plans:

- free
- pro
- team

All plans have `payment_enabled = False`. There is no payment processor and no real billing flow.

## 安全边界

V1.33 keeps the following boundaries:

- No broker connection.
- No automatic order placement.
- No generated real trade instruction.
- No stock price prediction.
- No AI API calls.
- No OpenAI API calls.
- No real payment processing.
- No real authentication system.
- No sensitive information storage.
- No core strategy logic changes.

## 非交易声明

This system remains a research and education product prototype. It does not provide investment advice, does not place trades, and does not connect to any brokerage.

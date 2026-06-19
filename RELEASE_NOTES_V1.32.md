# Release Notes V1.32

## SaaS-ready Foundation

V1.32 adds a release and SaaS-ready layer on top of the V1.31 platform architecture. It introduces deployment files, a versioned API, logical account isolation, a system admin panel, and platform configuration defaults.

## API 可用

The new `src/api/v2/` package exposes deployment-oriented endpoints with this stable response shape:

```json
{
  "success": true,
  "data": {},
  "meta": {
    "version": "V1.32",
    "latency_ms": 0
  },
  "warning": []
}
```

## Docker 部署

The `deploy/` directory includes:

- `Dockerfile`
- `docker-compose.yml`
- `.env.example`

Docker Compose can start both UI and API services without external credentials.

## 多用户结构

`src/core/account/` adds logical account isolation under:

```text
data/users/{user_id}/
```

Each user receives separate report, cache, and dashboard paths. This is not a login system.

## 插件架构

V1.32 keeps the V1.31 plugin architecture and uses it from the release API and system admin panel to report loaded plugin status.

## 安全边界

V1.32 keeps the existing research-only boundaries:

- No broker connection.
- No automatic order placement.
- No generated real trade instruction.
- No stock price prediction.
- No AI API calls.
- No OpenAI API calls.
- No saved key, credential, or credential-like value.
- No payment system.
- No real login system.
- No core strategy logic changes.

from __future__ import annotations

import os
from collections import defaultdict, deque
from time import time
from typing import Deque

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.v2.errors import RateLimitApiError


DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8501",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8501",
]


def allowed_origins() -> list[str]:
    configured = [
        origin.strip()
        for origin in os.getenv("SHANDONG_ALLOWED_ORIGINS", "").split(",")
        if origin.strip() and origin.strip() != "*"
    ]
    origins = DEFAULT_ALLOWED_ORIGINS + configured
    return list(dict.fromkeys(origins))


def configure_cors(app: FastAPI) -> FastAPI:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    return app


class InMemoryRateLimiter:
    def __init__(self, limit_per_minute: int = 120) -> None:
        self.limit_per_minute = max(int(limit_per_minute or 120), 1)
        self._events: dict[str, Deque[float]] = defaultdict(deque)

    def allow(self, user_id: str, now: float | None = None) -> bool:
        current = time() if now is None else float(now)
        key = str(user_id or "default")
        window = self._events[key]
        while window and current - window[0] >= 60:
            window.popleft()
        if len(window) >= self.limit_per_minute:
            return False
        window.append(current)
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: InMemoryRateLimiter | None = None) -> None:
        super().__init__(app)
        self.limiter = limiter or InMemoryRateLimiter()

    async def dispatch(self, request: Request, call_next):
        user_id = request.query_params.get("user_id", "default")
        if not self.limiter.allow(user_id):
            error = RateLimitApiError()
            return JSONResponse(status_code=error.status_code, content=error.to_response())
        return await call_next(request)

from __future__ import annotations

from time import perf_counter

from src.config.platform_config import PLATFORM_VERSION


def response_meta(started_at: float | None = None, meta: dict | None = None, status_code: int | None = None) -> dict:
    start = perf_counter() if started_at is None else float(started_at)
    latency_ms = max((perf_counter() - start) * 1000, 0.0)
    payload = {
        "version": PLATFORM_VERSION,
        "latency_ms": round(latency_ms, 2),
    }
    if meta:
        payload.update(meta)
    if status_code is not None:
        payload["status_code"] = int(status_code)
    return payload


def success_response(
    data: dict | list | None = None,
    meta: dict | None = None,
    warning: list[str] | None = None,
    started_at: float | None = None,
) -> dict:
    return {
        "success": True,
        "data": data if data is not None else {},
        "meta": response_meta(started_at=started_at, meta=meta),
        "warning": warning or [],
    }


def error_response(
    message: str,
    code: str = "API_ERROR",
    status_code: int = 400,
    detail: dict | None = None,
    started_at: float | None = None,
    meta: dict | None = None,
) -> dict:
    return {
        "success": False,
        "error": {
            "code": code or "API_ERROR",
            "message": str(message or "API error"),
            "detail": detail or {},
        },
        "meta": response_meta(started_at=started_at, meta=meta, status_code=status_code),
    }

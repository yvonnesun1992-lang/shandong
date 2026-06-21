from __future__ import annotations

from collections import deque
from datetime import UTC, datetime
from threading import Lock


_LOCK = Lock()
_API_METRICS: dict[str, dict] = {}
_TOTAL_REQUESTS = 0
_TOTAL_LATENCY_MS = 0.0
_TOTAL_WARNINGS = 0
_HEALTH_TIMELINE: deque[dict] = deque(maxlen=50)


def _safe_path(path: str) -> str:
    text = str(path or "unknown")
    if text.startswith("/") and not text.startswith("/api/"):
        return "redacted_path"
    if "\\" in text:
        return "redacted_path"
    return text[:160]


def record_api_metric(path: str, status: str, latency_ms: float, warning_count: int = 0) -> None:
    global _TOTAL_LATENCY_MS, _TOTAL_REQUESTS, _TOTAL_WARNINGS
    try:
        safe_path = _safe_path(path)
        safe_status = str(status or "unknown")[:32]
        latency = max(float(latency_ms or 0), 0.0)
        warnings = max(int(warning_count or 0), 0)
        with _LOCK:
            item = _API_METRICS.setdefault(
                safe_path,
                {
                    "count": 0,
                    "status_counts": {},
                    "warning_count": 0,
                    "average_latency_ms": 0.0,
                    "max_latency_ms": 0.0,
                    "total_latency_ms": 0.0,
                },
            )
            item["count"] += 1
            item["status_counts"][safe_status] = item["status_counts"].get(safe_status, 0) + 1
            item["warning_count"] += warnings
            item["total_latency_ms"] += latency
            item["average_latency_ms"] = round(item["total_latency_ms"] / item["count"], 2)
            item["max_latency_ms"] = round(max(item["max_latency_ms"], latency), 2)
            _TOTAL_REQUESTS += 1
            _TOTAL_LATENCY_MS += latency
            _TOTAL_WARNINGS += warnings
    except Exception:
        return


def get_api_metrics_summary() -> dict:
    with _LOCK:
        by_path = {
            path: {key: value for key, value in data.items() if key != "total_latency_ms"}
            for path, data in sorted(_API_METRICS.items())
        }
        return {
            "total_requests": _TOTAL_REQUESTS,
            "average_latency_ms": round(_TOTAL_LATENCY_MS / _TOTAL_REQUESTS, 2) if _TOTAL_REQUESTS else 0,
            "warning_count": _TOTAL_WARNINGS,
            "by_path": by_path,
        }


def reset_api_metrics() -> None:
    global _TOTAL_LATENCY_MS, _TOTAL_REQUESTS, _TOTAL_WARNINGS
    with _LOCK:
        _API_METRICS.clear()
        _HEALTH_TIMELINE.clear()
        _TOTAL_REQUESTS = 0
        _TOTAL_LATENCY_MS = 0.0
        _TOTAL_WARNINGS = 0


def record_health_snapshot(name: str, status: str, warning_count: int = 0, error_count: int = 0) -> None:
    try:
        snapshot = {
            "name": str(name or "unknown")[:80],
            "status": str(status or "unknown")[:32],
            "warning_count": max(int(warning_count or 0), 0),
            "error_count": max(int(error_count or 0), 0),
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat(),
        }
        with _LOCK:
            _HEALTH_TIMELINE.append(snapshot)
    except Exception:
        return


def get_health_timeline_summary() -> dict:
    with _LOCK:
        timeline = list(_HEALTH_TIMELINE)
    return {
        "total_snapshots": len(timeline),
        "latest": timeline[-1] if timeline else {},
        "items": timeline[-10:],
    }

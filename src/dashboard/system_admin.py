from __future__ import annotations

from time import perf_counter

from src.core.cache_manager import StrategyCacheManager
from src.plugins import PluginRegistry, create_default_registry
from src.system.health_check import run_system_health_check


def build_system_admin_panel(
    cache: StrategyCacheManager | None = None,
    registry: PluginRegistry | None = None,
    api_latency_ms: float | None = None,
    error_logs: list[str] | None = None,
) -> dict:
    started = perf_counter()
    cache = cache or StrategyCacheManager()
    registry = registry or create_default_registry()
    health = run_system_health_check()
    measured_latency = api_latency_ms if api_latency_ms is not None else (perf_counter() - started) * 1000
    cache_stats = cache.stats()
    health_score = 100 if health.get("status") == "ok" else 60

    return {
        "api_latency_ms": round(float(measured_latency), 2),
        "cache": cache_stats,
        "system_health_score": health_score,
        "system_health": health,
        "plugins": {
            "loaded": registry.names(),
            "count": len(registry.names()),
        },
        "error_logs": error_logs or [],
    }

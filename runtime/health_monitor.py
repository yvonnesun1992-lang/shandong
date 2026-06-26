from __future__ import annotations

import resource


class HealthMonitor:
    def __init__(
        self,
        max_execution_latency_ms: float = 500.0,
        max_signal_delay_ms: float = 500.0,
        max_memory_usage_mb: float = 2048.0,
    ) -> None:
        self.max_execution_latency_ms = float(max_execution_latency_ms)
        self.max_signal_delay_ms = float(max_signal_delay_ms)
        self.max_memory_usage_mb = float(max_memory_usage_mb)
        self.current = {
            "status": "HEALTHY",
            "latency": {"execution_ms": 0.0, "signal_delay_ms": 0.0},
            "memory": {"usage_mb": 0.0},
            "errors": 0,
            "engine_alive": False,
        }

    def update(
        self,
        engine_alive: bool,
        execution_latency_ms: float = 0.0,
        signal_delay_ms: float = 0.0,
        memory_usage_mb: float | None = None,
        error_count: int = 0,
    ) -> dict:
        memory = float(_memory_mb() if memory_usage_mb is None else memory_usage_mb)
        status = "HEALTHY"
        if not engine_alive:
            status = "FAILED"
        elif (
            execution_latency_ms > self.max_execution_latency_ms
            or signal_delay_ms > self.max_signal_delay_ms
            or memory > self.max_memory_usage_mb
            or error_count > 0
        ):
            status = "DEGRADED"
        self.current = {
            "status": status,
            "latency": {"execution_ms": float(execution_latency_ms), "signal_delay_ms": float(signal_delay_ms)},
            "memory": {"usage_mb": memory},
            "errors": int(error_count),
            "engine_alive": bool(engine_alive),
        }
        return self.current

    def snapshot(self) -> dict:
        return dict(self.current)


def _memory_mb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return float(usage / 1024 if usage > 10_000 else usage)


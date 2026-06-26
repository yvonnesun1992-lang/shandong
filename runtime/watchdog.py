from __future__ import annotations

import resource
import time


class Watchdog:
    def __init__(
        self,
        max_event_loop_delay_ms: float = 500.0,
        max_signal_latency_ms: float = 250.0,
        max_memory_usage_mb: float = 2048.0,
    ) -> None:
        self.max_event_loop_delay_ms = float(max_event_loop_delay_ms)
        self.max_signal_latency_ms = float(max_signal_latency_ms)
        self.max_memory_usage_mb = float(max_memory_usage_mb)
        self.last_check = time.monotonic()
        self.restart_count = 0

    def metrics(self, signal_latency_ms: float = 0.0) -> dict:
        now = time.monotonic()
        delay_ms = max((now - self.last_check) * 1000, 0.0)
        self.last_check = now
        return {
            "cpu_usage": 0.0,
            "memory_usage_mb": _memory_mb(),
            "event_loop_delay_ms": delay_ms,
            "signal_latency_ms": float(signal_latency_ms),
        }

    def check(self, engine, metrics: dict | None = None) -> dict:
        current = metrics or self.metrics()
        reason = ""
        if current.get("system_crash_detected"):
            reason = "SYSTEM_CRASH"
        elif float(current.get("event_loop_delay_ms", 0.0)) > self.max_event_loop_delay_ms:
            reason = "EVENT_LOOP_DELAY"
        elif float(current.get("signal_latency_ms", 0.0)) > self.max_signal_latency_ms:
            reason = "SIGNAL_LATENCY"
        elif float(current.get("memory_usage_mb", 0.0)) > self.max_memory_usage_mb:
            reason = "MEMORY_USAGE"
        if reason:
            self.restart_count += 1
            if hasattr(engine, "restart_engine"):
                engine.restart_engine()
            return {"status": "RESTARTED", "reason": reason, "metrics": current}
        return {"status": "OK", "reason": "OK", "metrics": current}


def _memory_mb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return float(usage / 1024 if usage > 10_000 else usage)


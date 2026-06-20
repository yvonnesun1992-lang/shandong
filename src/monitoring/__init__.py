from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.system.health_check import run_system_health_check


@dataclass
class MonitoringState:
    latencies: list[dict] = field(default_factory=list)
    logs: list[dict] = field(default_factory=list)
    usage_metrics: dict[str, int] = field(default_factory=dict)

    def log(self, level: str, message: str) -> None:
        self.logs.append(
            {
                "level": str(level),
                "message": str(message),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )


def track_api_latency(state: MonitoringState, endpoint: str, latency_ms: float) -> dict:
    entry = {"endpoint": str(endpoint), "latency_ms": round(float(latency_ms), 2)}
    state.latencies.append(entry)
    return entry


def track_usage_metric(state: MonitoringState, metric_name: str, value: int = 1) -> dict:
    metric = str(metric_name)
    state.usage_metrics[metric] = state.usage_metrics.get(metric, 0) + int(value)
    return {"metric": metric, "value": state.usage_metrics[metric]}


def build_health_snapshot(state: MonitoringState) -> dict:
    count = len(state.latencies)
    avg_ms = sum(item["latency_ms"] for item in state.latencies) / count if count else 0.0
    health = run_system_health_check()
    health_status = health.get("status") or health.get("overall_status", "warn")
    normalized_health = {**health, "status": health_status}
    return {
        "api_latency": {
            "count": count,
            "avg_ms": round(avg_ms, 2),
            "latest": state.latencies[-5:],
        },
        "logs": state.logs[-20:],
        "usage_metrics": dict(state.usage_metrics),
        "system_health": normalized_health,
    }

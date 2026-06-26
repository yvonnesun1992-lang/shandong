from __future__ import annotations


class RuntimeMonitor:
    def __init__(self) -> None:
        self.signal_count = 0
        self.execution_count = 0
        self.latencies: list[float] = []
        self.last_snapshot: dict = {}

    def record_signal(self) -> None:
        self.signal_count += 1

    def record_execution(self, latency_ms: float = 0.0) -> None:
        self.execution_count += 1
        self.latencies.append(float(latency_ms))

    def update_state(self, state: dict, pnl: dict) -> None:
        self.last_snapshot = {
            "current_equity": float(pnl.get("equity", 0.0)),
            "positions": state.get("positions", {}),
            "pnl": pnl,
            "signal_flow_rate": self.signal_count,
            "execution_latency": sum(self.latencies) / len(self.latencies) if self.latencies else 0.0,
            "trade_count": self.execution_count,
            "signal_count": self.signal_count,
        }

    def snapshot(self) -> dict:
        return dict(self.last_snapshot or {"signal_count": self.signal_count, "trade_count": self.execution_count})



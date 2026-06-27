from __future__ import annotations


class SystemController:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.status = "IDLE"

    def start_engine(self, max_ticks: int | None = None) -> dict:
        self.status = "RUNNING"
        result = self.engine.run(max_ticks=max_ticks)
        self.status = result["status"]
        return result

    def stop_engine(self) -> None:
        self.status = "STOPPED"
        self.engine.market.close_market()

    def pause_engine(self) -> None:
        self.status = "PAUSED"

    def resume_engine(self) -> None:
        self.status = "RUNNING"

    def emergency_stop(self) -> None:
        self.engine.risk_gate.trigger_kill_switch("EMERGENCY_STOP")
        self.stop_engine()


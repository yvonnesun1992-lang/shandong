from __future__ import annotations


class ModeManager:
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"
    SAFE_MODE = "SAFE_MODE"

    def __init__(self, error_threshold: int = 3, drawdown_threshold: float = 0.10) -> None:
        self.error_threshold = int(error_threshold)
        self.drawdown_threshold = float(drawdown_threshold)
        self.mode = self.NORMAL
        self.error_count = 0
        self.reasons: list[str] = []

    def set_mode(self, mode: str, reason: str = "") -> str:
        self.mode = mode
        if reason:
            self.reasons.append(reason)
        return self.mode

    def record_error(self, reason: str) -> str:
        self.error_count += 1
        if self.error_count >= self.error_threshold:
            return self.set_mode(self.SAFE_MODE, reason)
        return self.set_mode(self.DEGRADED, reason)

    def evaluate_risk(self, risk: dict) -> str:
        if float(risk.get("drawdown", 0.0)) > self.drawdown_threshold:
            return self.set_mode(self.SAFE_MODE, "HIGH_DRAWDOWN")
        if risk.get("execution_failure"):
            return self.set_mode(self.SAFE_MODE, "EXECUTION_FAILURE")
        return self.mode


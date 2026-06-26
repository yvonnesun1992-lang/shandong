from __future__ import annotations

from runtime.logger import ProductionLogger
from runtime.mode_manager import ModeManager


class ErrorHandler:
    def __init__(self, logger: ProductionLogger | None = None, mode_manager: ModeManager | None = None) -> None:
        self.logger = logger or ProductionLogger()
        self.mode_manager = mode_manager or ModeManager()
        self.error_count = 0

    def handle(self, exc: Exception, context: dict | None = None) -> dict:
        self.error_count += 1
        mode = self.mode_manager.record_error(type(exc).__name__)
        self.logger.log(
            "ERROR",
            {
                "error_type": type(exc).__name__,
                "message": str(exc),
                "context": context or {},
                "mode": mode,
            },
        )
        return {"handled": True, "mode": mode, "error_count": self.error_count}


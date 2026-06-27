from __future__ import annotations

import time


class FaultInjector:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = bool(enabled)

    def apply_market_fault(self, tick: dict, index: int) -> dict | None:
        if not self.enabled:
            return tick
        if index > 0 and index % 97 == 0:
            return None
        mutated = dict(tick)
        if index > 0 and index % 131 == 0:
            mutated["close"] = float(mutated["close"]) * 1.25
        return mutated

    def signal_fault(self, index: int) -> None:
        if self.enabled and index > 0 and index % 89 == 0:
            raise RuntimeError("injected signal error")

    def execution_fault(self, index: int) -> None:
        if self.enabled and index > 0 and index % 149 == 0:
            raise RuntimeError("injected execution error")

    def latency_delay(self, index: int) -> float:
        if self.enabled and index > 0 and index % 113 == 0:
            time.sleep(0.001)
            return 250.0
        return 0.0

    def memory_warning(self, index: int) -> bool:
        return bool(self.enabled and index > 0 and index % 157 == 0)

    def forced_exception(self, index: int) -> None:
        if self.enabled and index > 0 and index % 211 == 0:
            raise RuntimeError("injected forced exception")



from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PluginBase:
    name: str
    description: str

    def run(self, payload: dict | None = None) -> dict:
        return {
            "status": "success",
            "plugin": self.name,
            "data": payload or {},
            "warning": [],
        }

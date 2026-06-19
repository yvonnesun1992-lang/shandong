from __future__ import annotations

from src.plugins.base import PluginBase


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginBase] = {}

    def register(self, plugin: PluginBase) -> None:
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> PluginBase | None:
        return self._plugins.get(str(name))

    def names(self) -> list[str]:
        return sorted(self._plugins)

    def run(self, name: str, payload: dict | None = None) -> dict:
        plugin = self.get(name)
        if plugin is None:
            return {"status": "error", "plugin": name, "data": {}, "warning": [f"Plugin not found: {name}"]}
        return plugin.run(payload or {})

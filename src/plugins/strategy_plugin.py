from __future__ import annotations

from src.plugins.base import PluginBase


class StrategyPlugin(PluginBase):
    def __init__(self) -> None:
        super().__init__("strategy", "Strategy research plugin")

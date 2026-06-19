from __future__ import annotations

from src.plugins.base import PluginBase


class RiskPlugin(PluginBase):
    def __init__(self) -> None:
        super().__init__("risk", "Risk research plugin")

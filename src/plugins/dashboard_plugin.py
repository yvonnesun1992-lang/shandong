from __future__ import annotations

from src.plugins.base import PluginBase


class DashboardPlugin(PluginBase):
    def __init__(self) -> None:
        super().__init__("dashboard", "Dashboard summary plugin")

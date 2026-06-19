from __future__ import annotations

from src.plugins.base import PluginBase


class ReportPlugin(PluginBase):
    def __init__(self) -> None:
        super().__init__("report", "Research report plugin")

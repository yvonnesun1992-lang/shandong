from __future__ import annotations

from src.plugins.base import PluginBase
from src.plugins.dashboard_plugin import DashboardPlugin
from src.plugins.registry import PluginRegistry
from src.plugins.report_plugin import ReportPlugin
from src.plugins.risk_plugin import RiskPlugin
from src.plugins.strategy_plugin import StrategyPlugin


def create_default_registry() -> PluginRegistry:
    registry = PluginRegistry()
    for plugin in [ReportPlugin(), StrategyPlugin(), RiskPlugin(), DashboardPlugin()]:
        registry.register(plugin)
    return registry


__all__ = [
    "DashboardPlugin",
    "PluginBase",
    "PluginRegistry",
    "ReportPlugin",
    "RiskPlugin",
    "StrategyPlugin",
    "create_default_registry",
]

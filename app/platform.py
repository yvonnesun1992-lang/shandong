from __future__ import annotations

from src.api.server import create_api_app
from src.core.cache_manager import StrategyCacheManager
from src.core.user_context import UserContext
from src.plugins import create_default_registry


def initialize_platform(user_id: str = "default") -> dict:
    """Initialize platform components in INIT -> CONFIG -> CACHE -> PLUGINS -> API -> UI order."""
    steps = ["INIT", "CONFIG", "CACHE", "PLUGINS", "API", "UI"]
    user_context = UserContext(user_id)
    cache = StrategyCacheManager(default_ttl_seconds=900)
    plugins = create_default_registry()
    api_app = create_api_app()
    return {
        "status": "ready",
        "steps": steps,
        "user_context": user_context,
        "cache": cache,
        "plugins": plugins,
        "api_app": api_app,
        "ui_entry": "app/main.py",
        "warning": [],
    }


if __name__ == "__main__":
    platform = initialize_platform()
    print(f"Platform initialized: {platform['status']}")

from __future__ import annotations

import os


DEFAULT_PLAN_LIMITS = {
    "free": {
        "max_reports_per_day": 10,
        "max_api_calls_per_day": 500,
        "max_api_keys": 1,
        "max_workspace_members": 1,
        "max_workspaces": 1,
    },
    "pro": {
        "max_reports_per_day": 100,
        "max_api_calls_per_day": 5000,
        "max_api_keys": 5,
        "max_workspace_members": 5,
        "max_workspaces": 3,
    },
    "team": {
        "max_reports_per_day": 500,
        "max_api_calls_per_day": 30000,
        "max_api_keys": 20,
        "max_workspace_members": 20,
        "max_workspaces": 10,
    },
}


def normalize_plan_name(plan_name: str | None) -> str:
    plan = str(plan_name or "free").strip().lower()
    return plan if plan in DEFAULT_PLAN_LIMITS else "free"


def _env_limit(plan_name: str, key: str, default: int) -> int:
    env_name = f"SHANDONG_{plan_name.upper()}_{key.upper()}"
    try:
        value = int(os.getenv(env_name, str(default)))
    except (TypeError, ValueError):
        return default
    return value if value >= 0 else default


def get_plan_limits(plan_name: str | None) -> dict:
    plan = normalize_plan_name(plan_name)
    defaults = DEFAULT_PLAN_LIMITS[plan]
    return {key: _env_limit(plan, key, value) for key, value in defaults.items()}

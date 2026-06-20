from __future__ import annotations

from src.config import database_config
from src.config.plan_config import get_plan_limits as config_plan_limits
from src.config.plan_config import normalize_plan_name
from src.db.repository import BillingRepository, safe_identifier


def get_plan_limits(plan_name: str | None) -> dict:
    return config_plan_limits(plan_name)


def get_workspace_plan(workspace_id: str, database_url: str | None = None) -> dict:
    safe_workspace = safe_identifier(workspace_id)
    billing = BillingRepository(database_url or database_config.DATABASE_URL)
    plan = billing.get_user_plan(safe_workspace, workspace_id=safe_workspace)
    plan_name = normalize_plan_name(plan.get("plan_name") if plan else "free")
    return {
        "workspace_id": safe_workspace,
        "plan_name": plan_name,
        "status": plan.get("status", "mock_active") if plan else "mock_active",
        "limits": get_plan_limits(plan_name),
        "real_payment_enabled": False,
    }


def set_workspace_plan(workspace_id: str, plan_name: str, database_url: str | None = None) -> dict:
    safe_workspace = safe_identifier(workspace_id)
    normalized = normalize_plan_name(plan_name)
    BillingRepository(database_url or database_config.DATABASE_URL).set_user_plan(
        safe_workspace,
        normalized,
        status="mock_active",
        workspace_id=safe_workspace,
    )
    return get_workspace_plan(safe_workspace, database_url=database_url)

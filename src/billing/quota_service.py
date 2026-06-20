from __future__ import annotations

from datetime import UTC, datetime, time

from src.api.v2.errors import ApiError
from src.billing.plan_service import get_workspace_plan
from src.billing.usage_service import get_daily_usage, get_usage_summary
from src.config import database_config
from src.db.repository import safe_identifier
from src.db.usage_repository import UsageRepository


EVENT_LIMIT_KEYS = {
    "report_generate": "max_reports_per_day",
    "api_call": "max_api_calls_per_day",
}


def _period_bounds() -> tuple[str, str]:
    now = datetime.now(UTC)
    return datetime.combine(now.date(), time.min, tzinfo=UTC).isoformat(), datetime.combine(now.date(), time.max, tzinfo=UTC).isoformat()


def check_quota(workspace_id: str, event_type: str, quantity: int = 1, database_url: str | None = None) -> dict:
    safe_workspace = safe_identifier(workspace_id)
    plan = get_workspace_plan(safe_workspace, database_url=database_url)
    limits = plan["limits"]
    event = str(event_type or "unknown")
    limit_key = EVENT_LIMIT_KEYS.get(event)
    used = get_daily_usage(safe_workspace, event, database_url=database_url)
    limit = limits.get(limit_key) if limit_key else None
    allowed = True if limit is None else used + max(int(quantity or 0), 0) <= int(limit)
    return {
        "workspace_id": safe_workspace,
        "plan_name": plan["plan_name"],
        "event_type": event,
        "limit_key": limit_key,
        "used": used,
        "quantity": max(int(quantity or 0), 0),
        "limit": limit,
        "allowed": allowed,
    }


def require_quota(workspace_id: str, event_type: str, quantity: int = 1, database_url: str | None = None) -> dict:
    status = check_quota(workspace_id, event_type, quantity=quantity, database_url=database_url)
    if not status["allowed"]:
        raise ApiError(
            "Quota exceeded",
            code="QUOTA_EXCEEDED",
            status_code=403,
            detail={
                "workspace_id": status["workspace_id"],
                "event_type": status["event_type"],
                "used": status["used"],
                "limit": status["limit"],
            },
        )
    return status


def get_quota_status(workspace_id: str, database_url: str | None = None) -> dict:
    safe_workspace = safe_identifier(workspace_id)
    plan = get_workspace_plan(safe_workspace, database_url=database_url)
    usage = get_usage_summary(safe_workspace, database_url=database_url)
    start, end = _period_bounds()
    snapshot = UsageRepository(database_url or database_config.DATABASE_URL).save_quota_snapshot(
        workspace_id=safe_workspace,
        plan_name=plan["plan_name"],
        period_start=start,
        period_end=end,
        usage=usage,
        limits=plan["limits"],
    )
    return {
        "workspace_id": safe_workspace,
        "plan": plan,
        "usage": usage,
        "limits": plan["limits"],
        "snapshot_id": snapshot["id"],
    }

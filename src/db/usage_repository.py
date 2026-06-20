from __future__ import annotations

from datetime import UTC, datetime, time
from uuid import uuid4

from src.db.base import decode_json, encode_json, utc_now_iso
from src.db.repository import BaseRepository, safe_identifier
from src.db.session import get_connection
from src.security.sanitizer import sanitize_response_payload


def _row_to_usage(row) -> dict | None:
    if row is None:
        return None
    data = dict(row)
    data["metadata_json"] = decode_json(data.get("metadata_json"))
    return data


def _row_to_snapshot(row) -> dict | None:
    if row is None:
        return None
    data = dict(row)
    data["usage_json"] = decode_json(data.get("usage_json"))
    data["limits_json"] = decode_json(data.get("limits_json"))
    return data


def _day_bounds(day: datetime | None = None) -> tuple[str, str]:
    value = day or datetime.now(UTC)
    start = datetime.combine(value.date(), time.min, tzinfo=UTC).isoformat()
    end = datetime.combine(value.date(), time.max, tzinfo=UTC).isoformat()
    return start, end


class UsageRepository(BaseRepository):
    def add_usage_event(
        self,
        workspace_id: str,
        user_id: str,
        event_type: str,
        quantity: int = 1,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict | list | str | None = None,
        event_id: str | None = None,
    ) -> dict:
        now = utc_now_iso()
        safe_workspace = safe_identifier(workspace_id)
        safe_user = safe_identifier(user_id)
        safe_event = safe_identifier(event_id or f"{safe_workspace}-{safe_user}-{event_type}-{uuid4().hex}", fallback="usage-event")
        safe_metadata = sanitize_response_payload(metadata or {})
        with get_connection(self.database_url) as connection:
            connection.execute(
                """
                insert into usage_events(
                    event_id, workspace_id, user_id, event_type, resource_type, resource_id,
                    quantity, created_at, metadata_json
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    safe_event,
                    safe_workspace,
                    safe_user,
                    event_type or "unknown",
                    resource_type or "",
                    safe_identifier(resource_id, "resource") if resource_id else "",
                    max(int(quantity or 0), 0),
                    now,
                    encode_json(safe_metadata),
                ),
            )
            row = connection.execute("select * from usage_events where event_id = ?", (safe_event,)).fetchone()
        usage = _row_to_usage(row)
        if usage is None:
            raise RuntimeError("usage event was not saved")
        return usage

    def list_usage_events(self, workspace_id: str, user_id: str | None = None, event_type: str | None = None) -> list[dict]:
        where = ["workspace_id = ?"]
        params: list = [safe_identifier(workspace_id)]
        if user_id is not None:
            where.append("user_id = ?")
            params.append(safe_identifier(user_id))
        if event_type is not None:
            where.append("event_type = ?")
            params.append(str(event_type))
        with get_connection(self.database_url) as connection:
            rows = connection.execute(
                f"select * from usage_events where {' and '.join(where)} order by created_at asc, id asc",
                tuple(params),
            ).fetchall()
        return [_row_to_usage(row) for row in rows if row is not None]

    def count_usage(self, workspace_id: str, event_type: str, start_at: str | None = None, end_at: str | None = None) -> int:
        where = ["workspace_id = ?", "event_type = ?"]
        params: list = [safe_identifier(workspace_id), str(event_type)]
        if start_at is not None:
            where.append("created_at >= ?")
            params.append(start_at)
        if end_at is not None:
            where.append("created_at <= ?")
            params.append(end_at)
        with get_connection(self.database_url) as connection:
            row = connection.execute(
                f"select coalesce(sum(quantity), 0) as total from usage_events where {' and '.join(where)}",
                tuple(params),
            ).fetchone()
        return int(row["total"] or 0) if row else 0

    def get_daily_usage(self, workspace_id: str, event_type: str, day: datetime | None = None) -> int:
        start, end = _day_bounds(day)
        return self.count_usage(workspace_id, event_type, start_at=start, end_at=end)

    def save_quota_snapshot(
        self,
        workspace_id: str,
        plan_name: str,
        period_start: str,
        period_end: str,
        usage: dict,
        limits: dict,
    ) -> dict:
        now = utc_now_iso()
        with get_connection(self.database_url) as connection:
            cursor = connection.execute(
                """
                insert into quota_snapshots(workspace_id, plan_name, period_start, period_end, usage_json, limits_json, created_at)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    safe_identifier(workspace_id),
                    plan_name or "free",
                    period_start,
                    period_end,
                    encode_json(usage),
                    encode_json(limits),
                    now,
                ),
            )
            row = connection.execute("select * from quota_snapshots where id = ?", (cursor.lastrowid,)).fetchone()
        snapshot = _row_to_snapshot(row)
        if snapshot is None:
            raise RuntimeError("quota snapshot was not saved")
        return snapshot

    def get_latest_quota_snapshot(self, workspace_id: str) -> dict | None:
        with get_connection(self.database_url) as connection:
            row = connection.execute(
                "select * from quota_snapshots where workspace_id = ? order by created_at desc, id desc limit 1",
                (safe_identifier(workspace_id),),
            ).fetchone()
        return _row_to_snapshot(row)

from __future__ import annotations

import hashlib
import re
from typing import Any

from src.config.database_config import DATABASE_URL
from src.db.base import decode_json, encode_json, utc_now_iso
from src.db.migrations import initialize_database
from src.db.session import get_connection


SAFE_ID_PATTERN = re.compile(r"[^A-Za-z0-9_.:@-]+")


def safe_identifier(value: str | None, fallback: str = "default") -> str:
    clean = SAFE_ID_PATTERN.sub("_", str(value or fallback).strip())
    clean = clean.strip("._")
    return clean or fallback


def row_to_dict(row: Any) -> dict | None:
    if row is None:
        return None
    return dict(row)


def report_row_to_dict(row: Any) -> dict | None:
    data = row_to_dict(row)
    if data is None:
        return None
    data["report_json"] = decode_json(data.get("report_json"))
    return data


def audit_row_to_dict(row: Any) -> dict | None:
    data = row_to_dict(row)
    if data is None:
        return None
    data["metadata_json"] = decode_json(data.get("metadata_json"))
    return data


def session_row_to_dict(row: Any) -> dict | None:
    data = row_to_dict(row)
    if data is None:
        return None
    data["metadata_json"] = decode_json(data.get("metadata_json"))
    return data


def hash_access_key_value(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


class BaseRepository:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or DATABASE_URL
        initialize_database(self.database_url)


class UserRepository(BaseRepository):
    def create_user(
        self,
        user_id: str,
        email: str | None = None,
        role: str = "user",
        plan: str = "free",
        is_active: bool = True,
        workspace_id: str = "default",
    ) -> dict:
        now = utc_now_iso()
        safe_user_id = safe_identifier(user_id)
        safe_workspace_id = safe_identifier(workspace_id)
        with get_connection(self.database_url) as connection:
            connection.execute(
                """
                insert into users(user_id, workspace_id, email, role, plan, created_at, updated_at, is_active)
                values (?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(user_id) do update set
                    workspace_id = excluded.workspace_id,
                    email = excluded.email,
                    role = excluded.role,
                    plan = excluded.plan,
                    updated_at = excluded.updated_at,
                    is_active = excluded.is_active
                """,
                (safe_user_id, safe_workspace_id, email, role or "user", plan or "free", now, now, 1 if is_active else 0),
            )
        user = self.get_user_by_user_id(safe_user_id)
        if user is None:
            raise RuntimeError("user was not created")
        return user

    def get_user_by_user_id(self, user_id: str) -> dict | None:
        with get_connection(self.database_url) as connection:
            row = connection.execute("select * from users where user_id = ?", (safe_identifier(user_id),)).fetchone()
        return row_to_dict(row)

    def list_users(self) -> list[dict]:
        with get_connection(self.database_url) as connection:
            rows = connection.execute("select * from users order by created_at asc, id asc").fetchall()
        return [dict(row) for row in rows]


class StrategyReportRepository(BaseRepository):
    def save_report(
        self,
        user_id: str,
        strategy_name: str | None = None,
        report_id: str | None = None,
        research_view: str | None = None,
        quality_score: float | int | None = None,
        quality_level: str | None = None,
        generated_at: str | None = None,
        saved_at: str | None = None,
        report_json: dict | list | str | None = None,
        markdown: str | None = None,
        workspace_id: str = "default",
    ) -> dict:
        now = utc_now_iso()
        safe_user_id = safe_identifier(user_id)
        safe_workspace_id = safe_identifier(workspace_id)
        safe_report_id = safe_identifier(report_id or f"{safe_user_id}-{now}", fallback=f"{safe_user_id}-report")
        with get_connection(self.database_url) as connection:
            connection.execute(
                """
                insert into strategy_reports(
                    report_id, user_id, workspace_id, strategy_name, research_view, quality_score, quality_level,
                    generated_at, saved_at, report_json, markdown, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(report_id) do update set
                    user_id = excluded.user_id,
                    workspace_id = excluded.workspace_id,
                    strategy_name = excluded.strategy_name,
                    research_view = excluded.research_view,
                    quality_score = excluded.quality_score,
                    quality_level = excluded.quality_level,
                    generated_at = excluded.generated_at,
                    saved_at = excluded.saved_at,
                    report_json = excluded.report_json,
                    markdown = excluded.markdown
                """,
                (
                    safe_report_id,
                    safe_user_id,
                    safe_workspace_id,
                    strategy_name or "unknown_strategy",
                    research_view or "",
                    quality_score,
                    quality_level or "",
                    generated_at or now,
                    saved_at or now,
                    encode_json(report_json),
                    markdown or "",
                    now,
                ),
            )
        report = self.get_report(safe_report_id, user_id=safe_user_id)
        if report is None:
            raise RuntimeError("report was not saved")
        return report

    def get_report(self, report_id: str, user_id: str | None = None, workspace_id: str | None = None) -> dict | None:
        safe_report_id = safe_identifier(report_id)
        params: tuple = (safe_report_id,)
        where = "report_id = ?"
        if user_id is not None:
            where += " and user_id = ?"
            params = (safe_report_id, safe_identifier(user_id))
        if workspace_id is not None:
            where += " and workspace_id = ?"
            params = (*params, safe_identifier(workspace_id))
        with get_connection(self.database_url) as connection:
            row = connection.execute(f"select * from strategy_reports where {where}", params).fetchone()
        return report_row_to_dict(row)

    def list_reports_by_user(self, user_id: str, workspace_id: str | None = None) -> list[dict]:
        where = "user_id = ?"
        params: tuple = (safe_identifier(user_id),)
        if workspace_id is not None:
            where += " and workspace_id = ?"
            params = (*params, safe_identifier(workspace_id))
        with get_connection(self.database_url) as connection:
            rows = connection.execute(
                f"select * from strategy_reports where {where} order by saved_at desc, id desc",
                params,
            ).fetchall()
        return [report_row_to_dict(row) for row in rows if row is not None]

    def delete_report(self, report_id: str, user_id: str | None = None, workspace_id: str | None = None) -> bool:
        safe_report_id = safe_identifier(report_id)
        params: tuple = (safe_report_id,)
        where = "report_id = ?"
        if user_id is not None:
            where += " and user_id = ?"
            params = (safe_report_id, safe_identifier(user_id))
        if workspace_id is not None:
            where += " and workspace_id = ?"
            params = (*params, safe_identifier(workspace_id))
        with get_connection(self.database_url) as connection:
            cursor = connection.execute(f"delete from strategy_reports where {where}", params)
            return cursor.rowcount > 0


class ApiKeyRepository(BaseRepository):
    def create_api_key_record(
        self,
        user_id: str,
        key_id: str,
        key_hash: str | None = None,
        key_value: str | None = None,
        status: str = "active",
        workspace_id: str = "default",
    ) -> dict:
        if key_hash is None and key_value is None:
            raise ValueError("key_hash or key_value is required")
        stored_hash = key_hash or hash_access_key_value(str(key_value))
        safe_workspace_id = safe_identifier(workspace_id)
        now = utc_now_iso()
        with get_connection(self.database_url) as connection:
            connection.execute(
                """
                insert into api_keys(user_id, workspace_id, key_id, key_hash, status, created_at, usage_count)
                values (?, ?, ?, ?, ?, ?, 0)
                on conflict(key_id) do update set
                    workspace_id = excluded.workspace_id,
                    status = excluded.status,
                    key_hash = excluded.key_hash
                """,
                (safe_identifier(user_id), safe_workspace_id, safe_identifier(key_id, "key"), stored_hash, status or "active", now),
            )
        records = [record for record in self.list_api_keys_by_user(user_id) if record["key_id"] == safe_identifier(key_id, "key")]
        if not records:
            raise RuntimeError("api key record was not saved")
        return records[0]

    def revoke_api_key(self, key_id: str, user_id: str | None = None) -> bool:
        now = utc_now_iso()
        safe_key_id = safe_identifier(key_id, "key")
        params: tuple = (now, safe_key_id)
        where = "key_id = ?"
        if user_id is not None:
            where += " and user_id = ?"
            params = (now, safe_key_id, safe_identifier(user_id))
        with get_connection(self.database_url) as connection:
            cursor = connection.execute(f"update api_keys set status = 'revoked', revoked_at = ? where {where}", params)
            return cursor.rowcount > 0

    def list_api_keys_by_user(self, user_id: str, workspace_id: str | None = None) -> list[dict]:
        where = "user_id = ?"
        params: tuple = (safe_identifier(user_id),)
        if workspace_id is not None:
            where += " and workspace_id = ?"
            params = (*params, safe_identifier(workspace_id))
        with get_connection(self.database_url) as connection:
            rows = connection.execute(
                f"select * from api_keys where {where} order by created_at desc, id desc",
                params,
            ).fetchall()
        return [dict(row) for row in rows]


class BillingRepository(BaseRepository):
    def get_user_plan(self, user_id: str, workspace_id: str | None = None) -> dict | None:
        where = "user_id = ?"
        params: tuple = (safe_identifier(user_id),)
        if workspace_id is not None:
            where += " and workspace_id = ?"
            params = (*params, safe_identifier(workspace_id))
        with get_connection(self.database_url) as connection:
            row = connection.execute(f"select * from billing_plans where {where}", params).fetchone()
        return row_to_dict(row)

    def set_user_plan(
        self,
        user_id: str,
        plan_name: str,
        status: str = "mock_active",
        started_at: str | None = None,
        expires_at: str | None = None,
        workspace_id: str = "default",
    ) -> dict:
        start = started_at or utc_now_iso()
        safe_user_id = safe_identifier(user_id)
        safe_workspace_id = safe_identifier(workspace_id)
        with get_connection(self.database_url) as connection:
            connection.execute(
                """
                insert into billing_plans(user_id, workspace_id, plan_name, status, started_at, expires_at)
                values (?, ?, ?, ?, ?, ?)
                on conflict(user_id) do update set
                    workspace_id = excluded.workspace_id,
                    plan_name = excluded.plan_name,
                    status = excluded.status,
                    started_at = excluded.started_at,
                    expires_at = excluded.expires_at
                """,
                (safe_user_id, safe_workspace_id, plan_name or "free", status or "mock_active", start, expires_at),
            )
        plan = self.get_user_plan(safe_user_id, workspace_id=safe_workspace_id)
        if plan is None:
            raise RuntimeError("billing plan was not saved")
        return plan


class AuditLogRepository(BaseRepository):
    def add_log(
        self,
        user_id: str,
        action: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict | list | str | None = None,
        workspace_id: str = "default",
    ) -> dict:
        now = utc_now_iso()
        safe_workspace_id = safe_identifier(workspace_id)
        with get_connection(self.database_url) as connection:
            cursor = connection.execute(
                """
                insert into audit_logs(user_id, workspace_id, action, resource_type, resource_id, created_at, metadata_json)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    safe_identifier(user_id),
                    safe_workspace_id,
                    action or "unknown",
                    resource_type or "",
                    safe_identifier(resource_id, "resource") if resource_id else "",
                    now,
                    encode_json(metadata),
                ),
            )
            row_id = cursor.lastrowid
            row = connection.execute("select * from audit_logs where id = ?", (row_id,)).fetchone()
        log = audit_row_to_dict(row)
        if log is None:
            raise RuntimeError("audit log was not saved")
        return log

    def list_logs_by_user(self, user_id: str, workspace_id: str | None = None) -> list[dict]:
        where = "user_id = ?"
        params: tuple = (safe_identifier(user_id),)
        if workspace_id is not None:
            where += " and workspace_id = ?"
            params = (*params, safe_identifier(workspace_id))
        with get_connection(self.database_url) as connection:
            rows = connection.execute(
                f"select * from audit_logs where {where} order by created_at desc, id desc",
                params,
            ).fetchall()
        return [audit_row_to_dict(row) for row in rows if row is not None]


class UserSessionRepository(BaseRepository):
    def create_session_record(
        self,
        user_id: str,
        session_id_hash: str,
        expires_at: str,
        status: str = "active",
        metadata: dict | list | str | None = None,
        workspace_id: str = "default",
    ) -> dict:
        now = utc_now_iso()
        safe_workspace_id = safe_identifier(workspace_id)
        with get_connection(self.database_url) as connection:
            connection.execute(
                """
                insert into user_sessions(session_id, user_id, workspace_id, status, created_at, expires_at, last_seen_at, metadata_json)
                values (?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(session_id) do update set
                    user_id = excluded.user_id,
                    workspace_id = excluded.workspace_id,
                    status = excluded.status,
                    expires_at = excluded.expires_at,
                    last_seen_at = excluded.last_seen_at,
                    metadata_json = excluded.metadata_json
                """,
                (
                    str(session_id_hash),
                    safe_identifier(user_id),
                    safe_workspace_id,
                    status or "active",
                    now,
                    expires_at,
                    now,
                    encode_json(metadata),
                ),
            )
        record = self.get_session_by_hash(session_id_hash)
        if record is None:
            raise RuntimeError("session record was not saved")
        return record

    def get_session_by_hash(self, session_id_hash: str) -> dict | None:
        with get_connection(self.database_url) as connection:
            row = connection.execute("select * from user_sessions where session_id = ?", (str(session_id_hash),)).fetchone()
        return session_row_to_dict(row)

    def revoke_session_by_hash(self, session_id_hash: str) -> bool:
        now = utc_now_iso()
        with get_connection(self.database_url) as connection:
            cursor = connection.execute(
                "update user_sessions set status = 'revoked', revoked_at = ?, last_seen_at = ? where session_id = ?",
                (now, now, str(session_id_hash)),
            )
            return cursor.rowcount > 0

    def touch_session_by_hash(self, session_id_hash: str) -> None:
        now = utc_now_iso()
        with get_connection(self.database_url) as connection:
            connection.execute("update user_sessions set last_seen_at = ? where session_id = ?", (now, str(session_id_hash)))


class UserPermissionRepository(BaseRepository):
    def set_permissions(self, user_id: str, role: str, permissions: list[str], resource_type: str = "", workspace_id: str = "default") -> list[dict]:
        safe_user_id = safe_identifier(user_id)
        safe_workspace_id = safe_identifier(workspace_id)
        now = utc_now_iso()
        with get_connection(self.database_url) as connection:
            connection.execute("delete from user_permissions where user_id = ? and workspace_id = ?", (safe_user_id, safe_workspace_id))
            for permission in permissions:
                connection.execute(
                    """
                    insert into user_permissions(user_id, workspace_id, role, permission, resource_type, created_at)
                    values (?, ?, ?, ?, ?, ?)
                    on conflict(user_id, permission, resource_type) do update set
                        workspace_id = excluded.workspace_id,
                        role = excluded.role
                    """,
                    (safe_user_id, safe_workspace_id, role or "user", permission, resource_type or "", now),
                )
        return self.list_permissions(safe_user_id, workspace_id=safe_workspace_id)

    def list_permissions(self, user_id: str, workspace_id: str | None = None) -> list[dict]:
        where = "user_id = ?"
        params: tuple = (safe_identifier(user_id),)
        if workspace_id is not None:
            where += " and workspace_id = ?"
            params = (*params, safe_identifier(workspace_id))
        with get_connection(self.database_url) as connection:
            rows = connection.execute(
                f"select * from user_permissions where {where} order by permission asc",
                params,
            ).fetchall()
        return [dict(row) for row in rows]

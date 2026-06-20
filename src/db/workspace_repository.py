from __future__ import annotations

from src.db.base import decode_json, encode_json, utc_now_iso
from src.db.repository import BaseRepository, safe_identifier
from src.db.session import get_connection


VALID_WORKSPACE_ROLES = {"owner", "admin", "member", "viewer"}


def workspace_row_to_dict(row) -> dict | None:
    if row is None:
        return None
    data = dict(row)
    data["metadata_json"] = decode_json(data.get("metadata_json"))
    return data


class WorkspaceRepository(BaseRepository):
    def create_workspace(
        self,
        owner_user_id: str,
        name: str,
        workspace_id: str | None = None,
        status: str = "active",
        metadata: dict | list | str | None = None,
    ) -> dict:
        safe_owner = safe_identifier(owner_user_id)
        safe_workspace = safe_identifier(workspace_id or name or safe_owner, fallback="default")
        now = utc_now_iso()
        with get_connection(self.database_url) as connection:
            connection.execute(
                """
                insert into workspaces(workspace_id, name, owner_user_id, status, created_at, updated_at, metadata_json)
                values (?, ?, ?, ?, ?, ?, ?)
                on conflict(workspace_id) do update set
                    name = excluded.name,
                    owner_user_id = excluded.owner_user_id,
                    status = excluded.status,
                    updated_at = excluded.updated_at,
                    metadata_json = excluded.metadata_json
                """,
                (safe_workspace, name or safe_workspace, safe_owner, status or "active", now, now, encode_json(metadata)),
            )
        self.add_member(safe_workspace, safe_owner, role="owner", status="active")
        workspace = self.get_workspace(safe_workspace)
        if workspace is None:
            raise RuntimeError("workspace was not created")
        return workspace

    def get_workspace(self, workspace_id: str) -> dict | None:
        with get_connection(self.database_url) as connection:
            row = connection.execute(
                "select * from workspaces where workspace_id = ?",
                (safe_identifier(workspace_id),),
            ).fetchone()
        return workspace_row_to_dict(row)

    def list_workspaces_by_user(self, user_id: str) -> list[dict]:
        with get_connection(self.database_url) as connection:
            rows = connection.execute(
                """
                select w.*, m.role as member_role, m.status as member_status
                from workspaces w
                join workspace_members m on m.workspace_id = w.workspace_id
                where m.user_id = ? and m.status = 'active' and w.status = 'active'
                order by w.created_at asc, w.id asc
                """,
                (safe_identifier(user_id),),
            ).fetchall()
        return [workspace_row_to_dict(row) for row in rows if row is not None]

    def add_member(self, workspace_id: str, user_id: str, role: str = "member", status: str = "active") -> dict:
        safe_workspace = safe_identifier(workspace_id)
        safe_user = safe_identifier(user_id)
        normalized_role = role if role in VALID_WORKSPACE_ROLES else "member"
        now = utc_now_iso()
        with get_connection(self.database_url) as connection:
            connection.execute(
                """
                insert into workspace_members(workspace_id, user_id, role, status, created_at, updated_at)
                values (?, ?, ?, ?, ?, ?)
                on conflict(workspace_id, user_id) do update set
                    role = excluded.role,
                    status = excluded.status,
                    updated_at = excluded.updated_at
                """,
                (safe_workspace, safe_user, normalized_role, status or "active", now, now),
            )
            row = connection.execute(
                "select * from workspace_members where workspace_id = ? and user_id = ?",
                (safe_workspace, safe_user),
            ).fetchone()
        if row is None:
            raise RuntimeError("workspace member was not saved")
        return dict(row)

    def remove_member(self, workspace_id: str, user_id: str) -> bool:
        now = utc_now_iso()
        with get_connection(self.database_url) as connection:
            cursor = connection.execute(
                "update workspace_members set status = 'removed', updated_at = ? where workspace_id = ? and user_id = ?",
                (now, safe_identifier(workspace_id), safe_identifier(user_id)),
            )
            return cursor.rowcount > 0

    def list_members(self, workspace_id: str) -> list[dict]:
        with get_connection(self.database_url) as connection:
            rows = connection.execute(
                """
                select * from workspace_members
                where workspace_id = ? and status = 'active'
                order by id asc
                """,
                (safe_identifier(workspace_id),),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_member_role(self, workspace_id: str, user_id: str) -> str | None:
        with get_connection(self.database_url) as connection:
            row = connection.execute(
                """
                select role from workspace_members
                where workspace_id = ? and user_id = ? and status = 'active'
                """,
                (safe_identifier(workspace_id), safe_identifier(user_id)),
            ).fetchone()
        return str(row["role"]) if row else None

    def ensure_default_workspace(self, user_id: str = "default") -> dict:
        workspace = self.get_workspace("default")
        if workspace is None:
            workspace = self.create_workspace(user_id, "Default Workspace", workspace_id="default")
        if self.get_member_role("default", user_id) is None:
            self.add_member("default", user_id, role="owner" if safe_identifier(user_id) == "default" else "member")
        return workspace

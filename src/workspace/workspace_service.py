from __future__ import annotations

from src.api.v2.errors import ApiError
from src.config.database_config import DATABASE_URL
from src.db.repository import safe_identifier
from src.db.workspace_repository import WorkspaceRepository
from src.workspace.workspace_context import WorkspaceContext, permissions_for_workspace_role


ADMIN_WORKSPACE_ROLES = {"owner", "admin"}
ACCESS_WORKSPACE_ROLES = {"owner", "admin", "member", "viewer"}


def _repo(database_url: str | None = None) -> WorkspaceRepository:
    return WorkspaceRepository(database_url or DATABASE_URL)


def create_workspace(owner_user_id: str, name: str, workspace_id: str | None = None, database_url: str | None = None) -> dict:
    return _repo(database_url).create_workspace(owner_user_id=owner_user_id, name=name, workspace_id=workspace_id)


def ensure_default_workspace(user_id: str = "default", database_url: str | None = None) -> dict:
    return _repo(database_url).ensure_default_workspace(user_id=user_id)


def get_user_workspaces(user_id: str, database_url: str | None = None) -> list[dict]:
    repo = _repo(database_url)
    repo.ensure_default_workspace("default")
    return repo.list_workspaces_by_user(user_id)


def get_active_workspace(user_id: str, workspace_id: str | None = None, database_url: str | None = None) -> WorkspaceContext:
    safe_workspace = safe_identifier(workspace_id or "default")
    safe_user = safe_identifier(user_id)
    repo = _repo(database_url)
    if safe_workspace == "default":
        repo.ensure_default_workspace(safe_user)
    role = repo.get_member_role(safe_workspace, safe_user)
    if role is None and safe_workspace == "default":
        repo.add_member("default", safe_user, role="owner" if safe_user == "default" else "member")
        role = repo.get_member_role("default", safe_user)
    role = role or "viewer"
    return WorkspaceContext(
        workspace_id=safe_workspace,
        user_id=safe_user,
        role=role,
        permissions=permissions_for_workspace_role(role),
    )


def require_workspace_access(user_id: str, workspace_id: str, database_url: str | None = None) -> WorkspaceContext:
    context = get_active_workspace(user_id=user_id, workspace_id=workspace_id, database_url=database_url)
    if context.role not in ACCESS_WORKSPACE_ROLES:
        raise ApiError(
            "Workspace access denied",
            code="WORKSPACE_ACCESS_DENIED",
            status_code=403,
            detail={"workspace_id": context.workspace_id},
        )
    repo = _repo(database_url)
    if repo.get_member_role(context.workspace_id, context.user_id) is None:
        raise ApiError(
            "Workspace access denied",
            code="WORKSPACE_ACCESS_DENIED",
            status_code=403,
            detail={"workspace_id": context.workspace_id},
        )
    return context


def require_workspace_role(user_id: str, workspace_id: str, allowed_roles: set[str] | list[str], database_url: str | None = None) -> WorkspaceContext:
    context = require_workspace_access(user_id=user_id, workspace_id=workspace_id, database_url=database_url)
    if context.role not in set(allowed_roles):
        raise ApiError(
            "Workspace role denied",
            code="WORKSPACE_ROLE_DENIED",
            status_code=403,
            detail={"workspace_id": context.workspace_id, "allowed_roles": sorted(set(allowed_roles))},
        )
    return context

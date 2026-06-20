from __future__ import annotations

from src.api.v2.errors import ApiError
from src.config import database_config
from src.db.repository import UserPermissionRepository, UserRepository, safe_identifier


ROLE_PERMISSIONS = {
    "admin": ["report:read", "report:write", "dashboard:read", "risk:read", "admin:read", "api_key:manage"],
    "user": ["report:read", "report:write", "dashboard:read", "risk:read"],
    "viewer": ["report:read", "dashboard:read", "risk:read"],
}


def get_default_permissions(role: str) -> list[str]:
    return list(ROLE_PERMISSIONS.get(str(role or "user"), ROLE_PERMISSIONS["user"]))


def set_user_role(user_id: str, role: str = "user", plan: str = "free") -> dict:
    safe_user = safe_identifier(user_id)
    normalized_role = str(role or "user")
    UserRepository(database_config.DATABASE_URL).create_user(safe_user, role=normalized_role, plan=plan or "free")
    permissions = get_default_permissions(normalized_role)
    UserPermissionRepository(database_config.DATABASE_URL).set_permissions(safe_user, normalized_role, permissions)
    return {"user_id": safe_user, "role": normalized_role, "permissions": permissions}


def get_user_permissions(user_id: str) -> list[str]:
    safe_user = safe_identifier(user_id)
    try:
        rows = UserPermissionRepository(database_config.DATABASE_URL).list_permissions(safe_user)
        if rows:
            return [str(row["permission"]) for row in rows]
        user = UserRepository(database_config.DATABASE_URL).get_user_by_user_id(safe_user)
        if user:
            return get_default_permissions(user.get("role", "user"))
    except Exception:
        if safe_user == "default":
            return get_default_permissions("admin")
        return get_default_permissions("user")
    if safe_user == "default":
        return get_default_permissions("admin")
    return get_default_permissions("user")


def has_permission(user_id: str, permission: str) -> bool:
    return str(permission) in set(get_user_permissions(user_id))


def require_permission(user_id: str, permission: str) -> None:
    if has_permission(user_id, permission):
        return
    raise ApiError(
        "Permission denied",
        code="PERMISSION_DENIED",
        status_code=403,
        detail={"permission": str(permission)},
    )

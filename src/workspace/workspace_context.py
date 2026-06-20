from __future__ import annotations

from dataclasses import dataclass, field


WORKSPACE_ROLE_PERMISSIONS = {
    "owner": ["workspace:read", "workspace:write", "workspace:admin"],
    "admin": ["workspace:read", "workspace:write", "workspace:admin"],
    "member": ["workspace:read", "workspace:write"],
    "viewer": ["workspace:read"],
}


@dataclass(frozen=True)
class WorkspaceContext:
    workspace_id: str = "default"
    user_id: str = "default"
    role: str = "viewer"
    permissions: list[str] = field(default_factory=list)

    @property
    def is_owner(self) -> bool:
        return self.role == "owner"

    @property
    def is_admin(self) -> bool:
        return self.role in {"owner", "admin"}

    @property
    def is_member(self) -> bool:
        return self.role in {"owner", "admin", "member"}

    def as_dict(self) -> dict:
        return {
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "role": self.role,
            "permissions": list(self.permissions),
            "is_owner": self.is_owner,
            "is_admin": self.is_admin,
            "is_member": self.is_member,
        }


def permissions_for_workspace_role(role: str) -> list[str]:
    return list(WORKSPACE_ROLE_PERMISSIONS.get(str(role or "viewer"), WORKSPACE_ROLE_PERMISSIONS["viewer"]))

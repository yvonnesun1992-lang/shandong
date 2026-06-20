from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AuthContext:
    user_id: str = "default"
    role: str = "admin"
    plan: str = "free"
    permissions: list[str] = field(default_factory=list)
    session_id: str | None = None
    is_authenticated: bool = True
    workspace_id: str = "default"
    workspace_role: str = "owner"
    workspace_permissions: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "role": self.role,
            "plan": self.plan,
            "permissions": list(self.permissions),
            "session_id": self.session_id,
            "is_authenticated": self.is_authenticated,
            "workspace_id": self.workspace_id,
            "workspace_role": self.workspace_role,
            "workspace_permissions": list(self.workspace_permissions),
        }

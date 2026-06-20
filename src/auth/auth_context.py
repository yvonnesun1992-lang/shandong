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

    def as_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "role": self.role,
            "plan": self.plan,
            "permissions": list(self.permissions),
            "session_id": self.session_id,
            "is_authenticated": self.is_authenticated,
        }

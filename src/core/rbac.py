from __future__ import annotations

from dataclasses import dataclass, field


DEFAULT_PERMISSIONS = {
    "admin": {
        "report": {"read", "write"},
        "dashboard": {"read", "write"},
        "api": {"read", "write"},
    },
    "user": {
        "report": {"read", "write"},
        "dashboard": {"read"},
        "api": {"read"},
    },
    "viewer": {
        "report": {"read"},
        "dashboard": {"read"},
        "api": {"read"},
    },
}


@dataclass
class RBACPolicy:
    permissions: dict[str, dict[str, set[str]]] = field(default_factory=lambda: DEFAULT_PERMISSIONS)

    def allowed(self, role: str, resource: str, action: str) -> bool:
        role_permissions = self.permissions.get(str(role), {})
        resource_actions = role_permissions.get(str(resource), set())
        return str(action) in resource_actions


def can_access(user: object, resource: str, action: str, policy: RBACPolicy | None = None) -> bool:
    active_policy = policy or RBACPolicy()
    role = getattr(user, "role", "viewer")
    return active_policy.allowed(role, resource, action)


def require_permission(user: object, resource: str, action: str, policy: RBACPolicy | None = None) -> dict:
    allowed = can_access(user, resource, action, policy=policy)
    return {
        "allowed": allowed,
        "role": getattr(user, "role", "viewer"),
        "resource": resource,
        "action": action,
    }

from __future__ import annotations

from src.auth.permission_service import get_default_permissions


def initialize_auth_defaults(user_id: str = "default", role: str = "admin") -> dict:
    return {"user_id": user_id or "default", "role": role or "admin", "permissions": get_default_permissions(role)}

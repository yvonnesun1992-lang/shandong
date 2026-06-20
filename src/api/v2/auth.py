from __future__ import annotations

import logging
from typing import Any

from fastapi import Request

from src.api.v2.errors import ApiError
from src.auth.api_key_service import verify_api_key
from src.auth.auth_context import AuthContext
from src.auth.permission_service import get_default_permissions, get_user_permissions
from src.auth.session_service import get_session, is_session_active
from src.config import database_config
from src.db.repository import AuditLogRepository, UserRepository, safe_identifier


LOGGER = logging.getLogger("shandong.api.v2.auth")
AUTH_SENSITIVE_KEYS = {"secret", "token", "password", "api_key", "raw_key", "x-api-key"}


def sanitize_auth_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            if str(key).lower() in AUTH_SENSITIVE_KEYS:
                continue
            clean[str(key)] = sanitize_auth_metadata(item)
        return clean
    if isinstance(value, list):
        return [sanitize_auth_metadata(item) for item in value]
    text = str(value)
    if any(marker in text.lower() for marker in AUTH_SENSITIVE_KEYS):
        return "[redacted]"
    return value


def audit_auth_event(user_id: str, action: str, metadata: dict | None = None) -> dict:
    safe_user = safe_identifier(user_id)
    clean_metadata = sanitize_auth_metadata(metadata or {})
    try:
        AuditLogRepository(database_config.DATABASE_URL).add_log(
            user_id=safe_user,
            action=action,
            resource_type="auth",
            resource_id=safe_user,
            metadata=clean_metadata,
        )
        return {"logged": True}
    except Exception as exc:
        LOGGER.info("auth_audit_fallback", extra={"user_id": safe_user, "action": action, "error_type": type(exc).__name__})
        return {"logged": False}


def extract_user_id(request: Request) -> str:
    return safe_identifier(request.headers.get("X-User-ID") or request.query_params.get("user_id") or "default")


def extract_session_id(request: Request) -> str | None:
    return request.headers.get("X-Session-ID")


def extract_api_key(request: Request) -> str | None:
    return request.headers.get("X-API-Key")


def _user_role_plan(user_id: str) -> tuple[str, str]:
    try:
        user = UserRepository(database_config.DATABASE_URL).get_user_by_user_id(user_id)
    except Exception:
        user = None
    if user:
        return str(user.get("role") or "user"), str(user.get("plan") or "free")
    if user_id == "default":
        return "admin", "free"
    return "user", "free"


def build_auth_context(request: Request) -> AuthContext:
    header_user = extract_user_id(request)
    session_value = extract_session_id(request)
    key_value = extract_api_key(request)

    if session_value and is_session_active(session_value):
        session = get_session(session_value)
        if session:
            user_id = safe_identifier(session.get("user_id"))
            role, plan = _user_role_plan(user_id)
            return AuthContext(
                user_id=user_id,
                role=role,
                plan=plan,
                permissions=get_user_permissions(user_id),
                session_id=session.get("session_id"),
                is_authenticated=True,
            )

    if key_value and verify_api_key(header_user, key_value):
        audit_auth_event(header_user, "api_key.verify", {"verified": True})
        role, plan = _user_role_plan(header_user)
        return AuthContext(
            user_id=header_user,
            role=role,
            plan=plan,
            permissions=get_user_permissions(header_user),
            is_authenticated=True,
        )

    return AuthContext(
        user_id=header_user,
        role="admin",
        plan="free",
        permissions=get_default_permissions("admin"),
        session_id=None,
        is_authenticated=True,
    )


def require_auth(request: Request) -> AuthContext:
    return build_auth_context(request)


def require_permission(request: Request, permission: str) -> AuthContext:
    context = require_auth(request)
    if str(permission) not in set(context.permissions):
        audit_auth_event(context.user_id, "auth.permission_denied", {"permission": permission})
        raise ApiError(
            "Permission denied",
            code="PERMISSION_DENIED",
            status_code=403,
            detail={"permission": str(permission)},
        )
    return context

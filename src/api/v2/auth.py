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
from src.security.policy import can_use_local_admin_fallback, get_security_policy
from src.security.sanitizer import sanitize_response_payload


LOGGER = logging.getLogger("shandong.api.v2.auth")
AUTH_SENSITIVE_KEYS = {"secret", "token", "password", "api_key", "raw_key", "x-api-key", "session_id", "authorization", "bearer"}


def sanitize_auth_metadata(value: Any) -> Any:
    return sanitize_response_payload(value)


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


def _context_for_user(user_id: str, *, authenticated: bool, fallback_role: str | None = None, session_id: str | None = None) -> AuthContext:
    role, plan = _user_role_plan(user_id)
    if fallback_role and role == "user":
        role = fallback_role
    if fallback_role == "admin":
        role = "admin"
    permissions = get_default_permissions(role) if not authenticated and fallback_role else get_user_permissions(user_id)
    if fallback_role == "admin":
        permissions = get_default_permissions("admin")
    return AuthContext(
        user_id=user_id,
        role=role,
        plan=plan,
        permissions=permissions,
        session_id=session_id,
        is_authenticated=authenticated,
    )


def build_auth_context(request: Request) -> AuthContext:
    policy = get_security_policy()
    header_user = extract_user_id(request)
    session_value = extract_session_id(request)
    key_value = extract_api_key(request)

    audit_auth_event(header_user, "security.policy_checked", policy.as_dict())
    audit_auth_event(
        header_user,
        "auth.mode",
        {
            "auth_mode": policy.auth_mode,
            "require_auth": policy.require_auth,
            "allow_local_admin_fallback": policy.allow_local_admin_fallback,
        },
    )

    if session_value:
        if is_session_active(session_value):
            session = get_session(session_value)
            if session:
                user_id = safe_identifier(session.get("user_id"))
                audit_auth_event(user_id, "security.policy_checked", policy.as_dict())
                audit_auth_event(user_id, "auth.mode", {"auth_mode": policy.auth_mode, "require_auth": policy.require_auth})
                return _context_for_user(user_id, authenticated=True, session_id=session.get("session_id"))
        audit_auth_event(header_user, "auth.invalid_session", {"auth_mode": policy.auth_mode})
        raise ApiError("Invalid session", code="INVALID_SESSION", status_code=401)

    if key_value:
        if not verify_api_key(header_user, key_value):
            audit_auth_event(header_user, "auth.invalid_api_key", {"auth_mode": policy.auth_mode})
            raise ApiError("Invalid API key", code="INVALID_API_KEY", status_code=401)
        audit_auth_event(header_user, "api_key.verify", {"verified": True})
        audit_auth_event(header_user, "security.policy_checked", policy.as_dict())
        audit_auth_event(header_user, "auth.mode", {"auth_mode": policy.auth_mode, "require_auth": policy.require_auth})
        return _context_for_user(header_user, authenticated=True)

    if policy.auth_mode == "production":
        audit_auth_event(header_user, "auth.required", {"auth_mode": policy.auth_mode})
        raise ApiError("Authentication required", code="AUTH_REQUIRED", status_code=401)

    if policy.require_auth and not can_use_local_admin_fallback():
        audit_auth_event(header_user, "auth.required", {"auth_mode": policy.auth_mode})
        raise ApiError("Authentication required", code="AUTH_REQUIRED", status_code=401)

    if can_use_local_admin_fallback():
        return _context_for_user(header_user, authenticated=True, fallback_role="admin")

    return _context_for_user(header_user, authenticated=False, fallback_role="viewer")


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

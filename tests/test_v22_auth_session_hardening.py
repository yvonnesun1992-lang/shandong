from __future__ import annotations

import inspect
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def test_session_service_creates_hashes_revokes_and_expires(tmp_path, monkeypatch):
    from src.auth.session_service import (
        create_session,
        get_session,
        hash_session_value,
        is_session_active,
        revoke_session,
    )
    from src.config import database_config

    db_url = sqlite_url(tmp_path / "sessions.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)

    session = create_session("alice")
    fetched = get_session(session["session_id"])

    assert session["user_id"] == "alice"
    assert session["session_id"]
    assert hash_session_value(session["session_id"]) != session["session_id"]
    assert fetched is not None
    assert fetched["session_id"] != session["session_id"]
    assert is_session_active(session["session_id"]) is True
    assert revoke_session(session["session_id"]) is True
    assert is_session_active(session["session_id"]) is False


def test_session_expired_status_is_inactive(tmp_path, monkeypatch):
    from src.auth.session_service import create_session, is_session_active
    from src.config import database_config
    from src.db.session import get_connection

    db_url = sqlite_url(tmp_path / "expired.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)

    session = create_session("alice")
    expired_at = (datetime.now(UTC) - timedelta(minutes=1)).isoformat()
    with get_connection(db_url) as connection:
        connection.execute("update user_sessions set expires_at = ? where user_id = ?", (expired_at, "alice"))

    assert is_session_active(session["session_id"]) is False


def test_permission_service_defaults_and_requirements(tmp_path, monkeypatch):
    from src.api.v2.errors import ApiError
    from src.auth.permission_service import get_default_permissions, has_permission, require_permission, set_user_role
    from src.config import database_config

    db_url = sqlite_url(tmp_path / "permissions.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)

    assert "admin:read" in get_default_permissions("admin")
    assert "report:write" not in get_default_permissions("viewer")

    set_user_role("alice", "admin")
    set_user_role("viewer", "viewer")

    assert has_permission("alice", "admin:read") is True
    assert has_permission("viewer", "report:write") is False
    with pytest.raises(ApiError) as exc:
        require_permission("viewer", "report:write")
    assert exc.value.to_response()["error"]["code"] == "PERMISSION_DENIED"


def test_api_key_service_hashes_verifies_and_revokes(tmp_path, monkeypatch):
    from src.auth.api_key_service import create_api_key, hash_api_key, revoke_api_key, verify_api_key
    from src.config import database_config
    from src.db.repository import ApiKeyRepository

    db_url = sqlite_url(tmp_path / "keys.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)

    key = create_api_key("alice", key_id="key-1", raw_key="raw-local-key")
    records = ApiKeyRepository(db_url).list_api_keys_by_user("alice")

    assert hash_api_key("raw-local-key") != "raw-local-key"
    assert "raw-local-key" not in json.dumps(records)
    assert key["raw_key"] == "raw-local-key"
    assert verify_api_key("alice", "raw-local-key") is True
    assert revoke_api_key("alice", "key-1") is True
    assert verify_api_key("alice", "raw-local-key") is False


def test_auth_context_omits_raw_credentials():
    from src.auth.auth_context import AuthContext

    context = AuthContext(
        user_id="alice",
        role="admin",
        plan="pro",
        permissions=["report:read"],
        session_id="session-value",
        is_authenticated=True,
    )
    data = context.as_dict()

    assert data["user_id"] == "alice"
    assert data["is_authenticated"] is True
    assert "raw_key" not in json.dumps(data).lower()
    assert "token" not in json.dumps(data).lower()


def test_auth_api_login_logout_me_and_permission_checks(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config

    db_url = sqlite_url(tmp_path / "auth_api.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)
    client = TestClient(create_v2_api_app())

    login = client.post("/api/v2/auth/login", json={"user_id": "alice", "role": "admin"})
    assert login.status_code == 200
    session = login.json()["data"]["session"]
    assert session["user_id"] == "alice"
    assert session["role"] == "admin"
    assert session["session_id"]

    me = client.get("/api/v2/auth/me", headers={"X-Session-ID": session["session_id"]})
    assert me.status_code == 200
    me_text = json.dumps(me.json(), ensure_ascii=False).lower()
    assert me.json()["data"]["auth"]["user_id"] == "alice"
    assert "raw" not in me_text

    reports = client.get("/api/v2/reports/db-list", headers={"X-Session-ID": session["session_id"]})
    assert reports.status_code == 200
    assert reports.json()["success"] is True

    logout = client.post("/api/v2/auth/logout", json={"session_id": session["session_id"]})
    assert logout.status_code == 200
    assert logout.json()["data"]["revoked"] is True


def test_viewer_cannot_write_report_and_permission_denial_is_standard(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config

    db_url = sqlite_url(tmp_path / "viewer.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)
    client = TestClient(create_v2_api_app())

    login = client.post("/api/v2/auth/login", json={"user_id": "viewer", "role": "viewer"})
    session_id = login.json()["data"]["session"]["session_id"]
    denied = client.post("/api/v2/report/generate", json={"strategy_name": "trend_default"}, headers={"X-Session-ID": session_id})

    assert denied.status_code == 403
    body = denied.json()
    assert body["success"] is False
    assert body["error"]["code"] == "PERMISSION_DENIED"


def test_auth_audit_logs_are_sanitized(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config
    from src.db.repository import AuditLogRepository

    db_url = sqlite_url(tmp_path / "audit.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)
    client = TestClient(create_v2_api_app())

    login = client.post("/api/v2/auth/login", json={"user_id": "alice", "role": "admin", "secret": "abc"})
    session_id = login.json()["data"]["session"]["session_id"]
    client.get("/api/v2/auth/me", headers={"X-Session-ID": session_id, "X-API-Key": "raw-key"})
    client.post("/api/v2/auth/logout", json={"session_id": session_id, "password": "hidden"})

    logs = AuditLogRepository(db_url).list_logs_by_user("alice")
    text = json.dumps(logs, ensure_ascii=False).lower()

    assert any(log["action"] == "auth.login" for log in logs)
    assert any(log["action"] == "auth.logout" for log in logs)
    assert any(log["action"] == "auth.me" for log in logs)
    for forbidden in ["abc", "hidden", "raw-key", "password", "secret", "token", "api_key"]:
        assert forbidden not in text


def test_auth_source_keeps_safety_boundaries():
    import src.api.v2.auth as api_auth
    import src.auth.api_key_service as api_key_service
    import src.auth.auth_context as auth_context
    import src.auth.permission_service as permission_service
    import src.auth.session_service as session_service

    combined = "\n".join(
        [
            inspect.getsource(api_auth),
            inspect.getsource(api_key_service),
            inspect.getsource(auth_context),
            inspect.getsource(permission_service),
            inspect.getsource(session_service),
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto" + "order",
        "place_" + "order",
        "open" + "ai",
        "stripe_" + "secret",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in combined

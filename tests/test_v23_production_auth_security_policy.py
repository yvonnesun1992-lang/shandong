from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def configure_env(monkeypatch, tmp_path, auth_mode: str):
    from src.config import database_config

    monkeypatch.setenv("SHANDONG_AUTH_MODE", auth_mode)
    monkeypatch.setattr(database_config, "DATABASE_URL", sqlite_url(tmp_path / f"{auth_mode}.db"))


def test_default_auth_mode_is_local_and_allows_admin_fallback(monkeypatch):
    from src.security.policy import can_use_local_admin_fallback, get_security_policy

    monkeypatch.delenv("SHANDONG_AUTH_MODE", raising=False)
    policy = get_security_policy()

    assert policy.auth_mode == "local"
    assert policy.allow_local_admin_fallback is True
    assert can_use_local_admin_fallback() is True


def test_dev_mode_does_not_auto_promote_anonymous_admin(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path, "dev")
    client = TestClient(create_v2_api_app())

    response = client.get("/api/v2/admin/system", params={"user_id": "anonymous"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


def test_production_mode_blocks_anonymous_protected_endpoint(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.security.policy import can_use_local_admin_fallback, is_production_auth

    configure_env(monkeypatch, tmp_path, "production")
    client = TestClient(create_v2_api_app())

    response = client.get("/api/v2/reports/db-list")

    assert is_production_auth() is True
    assert can_use_local_admin_fallback() is False
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"


def test_production_valid_session_can_read_reports(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path, "production")
    client = TestClient(create_v2_api_app())

    login = client.post("/api/v2/auth/login", json={"user_id": "admin_user", "role": "admin"})
    session_id = login.json()["data"]["session"]["session_id"]
    response = client.get("/api/v2/reports/db-list", headers={"X-Session-ID": session_id})

    assert login.status_code == 200
    assert "mock_auth_only" in login.json()["warning"]
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_viewer_and_user_permissions_are_enforced_in_dev_and_production(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path, "production")
    client = TestClient(create_v2_api_app())
    viewer_login = client.post("/api/v2/auth/login", json={"user_id": "viewer", "role": "viewer"})
    user_login = client.post("/api/v2/auth/login", json={"user_id": "user", "role": "user"})

    viewer_session = viewer_login.json()["data"]["session"]["session_id"]
    user_session = user_login.json()["data"]["session"]["session_id"]
    viewer_write = client.post("/api/v2/report/generate", json={}, headers={"X-Session-ID": viewer_session})
    user_admin = client.get("/api/v2/admin/system", headers={"X-Session-ID": user_session})

    assert viewer_write.status_code == 403
    assert viewer_write.json()["error"]["code"] == "PERMISSION_DENIED"
    assert user_admin.status_code == 403
    assert user_admin.json()["error"]["code"] == "PERMISSION_DENIED"


def test_admin_can_access_admin_system_in_production(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path, "production")
    client = TestClient(create_v2_api_app())
    login = client.post("/api/v2/auth/login", json={"user_id": "admin", "role": "admin"})
    session_id = login.json()["data"]["session"]["session_id"]

    response = client.get("/api/v2/admin/system", headers={"X-Session-ID": session_id})

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_security_health_endpoint_returns_policy_summary(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path, "local")
    client = TestClient(create_v2_api_app())

    response = client.get("/api/v2/system/security-health")
    payload = response.json()["data"]["security"]

    assert response.status_code == 200
    assert payload["auth_mode"] == "local"
    assert payload["allow_local_admin_fallback"] is True
    assert payload["production_ready"] is False
    assert "local admin fallback enabled" in payload["warnings"]


def test_sanitizer_filters_sensitive_values_and_paths():
    from src.security.sanitizer import sanitize_exception_message, sanitize_response_payload, sanitize_sensitive_value

    payload = {
        "secret": "abc",
        "token": "def",
        "password": "ghi",
        "api_key": "raw-key",
        "raw_key": "raw",
        "session_id": "session",
        "authorization": "Bearer value",
        "nested": {"ok": True},
    }
    sanitized = sanitize_response_payload(payload)
    message = sanitize_exception_message("/Users/apple/project/data/shandong_v2.db token=abc")
    text = json.dumps({"sanitized": sanitized, "message": message, "single": sanitize_sensitive_value("Bearer secret")}).lower()

    for forbidden in ["abc", "def", "ghi", "raw-key", "session", "bearer", "/users/", "shandong_v2.db"]:
        assert forbidden not in text
    assert sanitized["nested"]["ok"] is True


def test_audit_log_does_not_store_raw_credentials(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config
    from src.db.repository import AuditLogRepository

    configure_env(monkeypatch, tmp_path, "production")
    client = TestClient(create_v2_api_app())
    login = client.post("/api/v2/auth/login", json={"user_id": "admin", "role": "admin", "password": "hidden"})
    session_id = login.json()["data"]["session"]["session_id"]
    client.get(
        "/api/v2/auth/me",
        headers={"X-Session-ID": session_id, "Authorization": "Bearer raw", "X-API-Key": "raw-key"},
    )

    logs = AuditLogRepository(database_config.DATABASE_URL).list_logs_by_user("admin")
    text = json.dumps(logs, ensure_ascii=False).lower()

    for forbidden in ["hidden", "raw-key", "bearer raw", "authorization", "password", "api_key"]:
        assert forbidden not in text
    assert any(log["action"] in {"auth.mode", "security.policy_checked", "auth.required"} for log in logs)


def test_invalid_session_and_invalid_api_key_return_standard_errors(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path, "production")
    client = TestClient(create_v2_api_app())

    invalid_session = client.get("/api/v2/reports/db-list", headers={"X-Session-ID": "bad-session"})
    invalid_key = client.get("/api/v2/reports/db-list", headers={"X-User-ID": "admin", "X-API-Key": "bad-key"})

    assert invalid_session.status_code == 401
    assert invalid_session.json()["error"]["code"] == "INVALID_SESSION"
    assert invalid_key.status_code == 401
    assert invalid_key.json()["error"]["code"] == "INVALID_API_KEY"


def test_security_source_keeps_boundaries():
    import src.api.v2.auth as api_auth
    import src.config.auth_config as auth_config
    import src.security.policy as policy
    import src.security.sanitizer as sanitizer

    combined = "\n".join(
        [
            inspect.getsource(api_auth),
            inspect.getsource(auth_config),
            inspect.getsource(policy),
            inspect.getsource(sanitizer),
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

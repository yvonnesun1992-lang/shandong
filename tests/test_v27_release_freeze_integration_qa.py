from __future__ import annotations

import inspect
import json
from pathlib import Path

from fastapi.testclient import TestClient


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def configure_env(monkeypatch, tmp_path, auth_mode: str) -> str:
    from src.config import database_config

    db_url = sqlite_url(tmp_path / f"v27-{auth_mode}.db")
    monkeypatch.setenv("SHANDONG_AUTH_MODE", auth_mode)
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)
    return db_url


def test_v2_integration_check_returns_success_structure(tmp_path, monkeypatch):
    from scripts.v2_integration_check import run_v2_integration_check
    from src.config import database_config

    original_database_url = database_config.DATABASE_URL
    monkeypatch.setenv("SHANDONG_AUTH_MODE", "local")
    monkeypatch.setattr(database_config, "DATABASE_URL", sqlite_url(tmp_path / "integration.db"))
    result = run_v2_integration_check()
    text = json.dumps(result, ensure_ascii=False).lower()

    assert set(result) == {"success", "checks", "warnings", "errors"}
    assert result["success"] is True
    assert isinstance(result["checks"], list)
    for forbidden in ["raw-key", "bearer raw", "password", "token", "api_key=", "/users/apple"]:
        assert forbidden not in text
    assert database_config.DATABASE_URL == sqlite_url(tmp_path / "integration.db")
    assert database_config.DATABASE_URL != original_database_url
    assert __import__("os").environ["SHANDONG_AUTH_MODE"] == "local"


def test_database_migrations_are_repeatable_and_default_workspace_exists(tmp_path):
    from src.db.migrations import initialize_database
    from src.db.workspace_repository import WorkspaceRepository

    db_url = sqlite_url(tmp_path / "migrations.db")
    first = initialize_database(db_url)
    second = initialize_database(db_url)
    workspace = WorkspaceRepository(db_url).ensure_default_workspace("default")

    assert first["status"] == "ok"
    assert second["status"] == "ok"
    assert workspace["workspace_id"] == "default"


def test_auth_modes_sessions_permissions_and_health_endpoints(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path, "local")
    local_client = TestClient(create_v2_api_app())
    local_auth = local_client.get("/api/v2/auth/me")
    assert local_auth.status_code == 200
    assert local_auth.json()["data"]["auth"]["role"] == "admin"

    configure_env(monkeypatch, tmp_path, "production")
    prod_client = TestClient(create_v2_api_app())
    anonymous = prod_client.get("/api/v2/reports/db-list")
    assert anonymous.status_code == 401
    assert anonymous.json()["error"]["code"] == "AUTH_REQUIRED"

    admin_login = prod_client.post("/api/v2/auth/login", json={"user_id": "admin", "role": "admin"})
    admin_session = admin_login.json()["data"]["session"]["session_id"]
    assert "mock_auth_only" in admin_login.json()["warning"]
    assert prod_client.get("/api/v2/reports/db-list", headers={"X-Session-ID": admin_session}).status_code == 200

    viewer_login = prod_client.post("/api/v2/auth/login", json={"user_id": "viewer", "role": "viewer"})
    viewer_session = viewer_login.json()["data"]["session"]["session_id"]
    viewer_write = prod_client.post("/api/v2/report/generate", json={}, headers={"X-Session-ID": viewer_session})
    assert viewer_write.status_code == 403
    assert viewer_write.json()["error"]["code"] == "PERMISSION_DENIED"

    user_login = prod_client.post("/api/v2/auth/login", json={"user_id": "user", "role": "user"})
    user_session = user_login.json()["data"]["session"]["session_id"]
    user_admin = prod_client.get("/api/v2/admin/system", headers={"X-Session-ID": user_session})
    assert user_admin.status_code == 403
    assert user_admin.json()["error"]["code"] == "PERMISSION_DENIED"

    for endpoint in [
        "/api/v2/system/readiness",
        "/api/v2/system/liveness",
        "/api/v2/system/security-health",
        "/api/v2/system/billing-health",
        "/api/v2/system/workspace-health",
    ]:
        response = prod_client.get(endpoint)
        assert response.status_code == 200
        assert response.json()["success"] is True


def test_workspace_isolation_and_quota_are_enforced(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.billing.usage_service import record_usage
    from src.config import database_config
    from src.db.workspace_repository import WorkspaceRepository

    configure_env(monkeypatch, tmp_path, "production")
    repo = WorkspaceRepository(database_config.DATABASE_URL)
    repo.create_workspace("alice", "Alpha", workspace_id="alpha")
    repo.create_workspace("bob", "Beta", workspace_id="beta")
    client = TestClient(create_v2_api_app())

    bob_login = client.post("/api/v2/auth/login", json={"user_id": "bob", "role": "admin"})
    bob_session = bob_login.json()["data"]["session"]["session_id"]
    blocked = client.get("/api/v2/reports/db-list", params={"workspace_id": "alpha"}, headers={"X-Session-ID": bob_session})
    assert blocked.status_code == 403
    assert blocked.json()["error"]["code"] == "WORKSPACE_ACCESS_DENIED"

    for _ in range(10):
        record_usage("default", "default", "report_generate")
    admin_login = client.post("/api/v2/auth/login", json={"user_id": "default", "role": "admin"})
    admin_session = admin_login.json()["data"]["session"]["session_id"]
    quota = client.post("/api/v2/report/generate", json={}, headers={"X-Session-ID": admin_session})
    assert quota.status_code == 403
    assert quota.json()["error"]["code"] == "QUOTA_EXCEEDED"


def test_startup_check_and_audit_logs_do_not_expose_raw_credentials(tmp_path, monkeypatch):
    from scripts.startup_check import run_startup_check
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config
    from src.db.repository import AuditLogRepository

    configure_env(monkeypatch, tmp_path, "production")
    startup = run_startup_check()
    assert startup["success"] is True
    assert "raw-key" not in json.dumps(startup, ensure_ascii=False).lower()

    client = TestClient(create_v2_api_app())
    login = client.post("/api/v2/auth/login", json={"user_id": "admin", "role": "admin"})
    session = login.json()["data"]["session"]["session_id"]
    client.get(
        "/api/v2/auth/me",
        headers={"X-Session-ID": session, "Authorization": "Bearer raw", "X-API-Key": "raw-key"},
    )
    logs = AuditLogRepository(database_config.DATABASE_URL).list_logs_by_user("admin")
    text = json.dumps(logs, ensure_ascii=False).lower()
    for forbidden in ["raw-key", "bearer raw", "authorization", "api_key", "password", "token"]:
        assert forbidden not in text


def test_v27_source_keeps_release_freeze_safety_boundaries():
    import scripts.v2_integration_check as integration_check

    source = inspect.getsource(integration_check).lower()
    forbidden = [
        "broker " + "api",
        "auto" + "order",
        "place_" + "order",
        "open" + "ai",
        "stripe_" + "secret",
        "live_" + "secret",
        "password=",
        "token=",
        "api_key=",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in source

from __future__ import annotations

import inspect
import json
from pathlib import Path

from fastapi.testclient import TestClient


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def configure_env(monkeypatch, tmp_path, auth_mode: str = "local") -> str:
    from src.config import database_config

    monkeypatch.setenv("SHANDONG_AUTH_MODE", auth_mode)
    db_url = sqlite_url(tmp_path / f"{auth_mode}.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)
    return db_url


def test_default_workspace_is_created_and_owner_is_member(tmp_path):
    from src.db.workspace_repository import WorkspaceRepository

    repo = WorkspaceRepository(sqlite_url(tmp_path / "workspace.db"))
    workspace = repo.ensure_default_workspace("default")
    members = repo.list_members("default")

    assert workspace["workspace_id"] == "default"
    assert repo.get_member_role("default", "default") == "owner"
    assert members[0]["user_id"] == "default"


def test_create_workspace_add_member_and_user_scoped_listing(tmp_path):
    from src.db.workspace_repository import WorkspaceRepository

    repo = WorkspaceRepository(sqlite_url(tmp_path / "members.db"))
    alpha = repo.create_workspace("alice", "Alpha Workspace", workspace_id="alpha")
    repo.add_member("alpha", "bob", role="member")
    repo.create_workspace("carol", "Carol Workspace", workspace_id="carol")

    assert alpha["owner_user_id"] == "alice"
    assert repo.get_member_role("alpha", "bob") == "member"
    assert [member["user_id"] for member in repo.list_members("alpha")] == ["alice", "bob"]
    assert {item["workspace_id"] for item in repo.list_workspaces_by_user("bob")} == {"alpha"}


def test_workspace_service_blocks_unauthorized_access(tmp_path):
    from src.api.v2.errors import ApiError
    from src.db.workspace_repository import WorkspaceRepository
    from src.workspace.workspace_service import require_workspace_access

    db_url = sqlite_url(tmp_path / "access.db")
    repo = WorkspaceRepository(db_url)
    repo.create_workspace("alice", "Alpha", workspace_id="alpha")

    try:
        require_workspace_access("bob", "alpha", database_url=db_url)
    except ApiError as exc:
        assert exc.status_code == 403
        assert exc.code == "WORKSPACE_ACCESS_DENIED"
    else:
        raise AssertionError("unauthorized workspace access should fail")


def test_auth_context_contains_workspace_fields_in_local_mode(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path, "local")
    client = TestClient(create_v2_api_app())

    response = client.get("/api/v2/auth/me", headers={"X-Workspace-ID": "default"})
    auth = response.json()["data"]["auth"]

    assert response.status_code == 200
    assert auth["workspace_id"] == "default"
    assert auth["workspace_role"] in {"owner", "admin"}
    assert "workspace_permissions" in auth


def test_workspace_api_and_health_return_standard_responses(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path, "local")
    client = TestClient(create_v2_api_app())

    created = client.post("/api/v2/workspaces", json={"workspace_id": "team-a", "name": "Team A", "owner_user_id": "alice"})
    listed = client.get("/api/v2/workspaces", params={"user_id": "alice"})
    health = client.get("/api/v2/system/workspace-health")

    assert created.status_code == 200
    assert created.json()["success"] is True
    assert listed.status_code == 200
    assert listed.json()["success"] is True
    assert listed.json()["data"]["workspaces"][0]["workspace_id"] == "team-a"
    assert health.status_code == 200
    assert health.json()["data"]["workspace"]["default_workspace_ready"] is True
    assert health.json()["data"]["workspace"]["workspace_isolation_enabled"] is True


def test_report_list_is_workspace_isolated(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config
    from src.db.repository import StrategyReportRepository
    from src.db.workspace_repository import WorkspaceRepository

    configure_env(monkeypatch, tmp_path, "local")
    repo = WorkspaceRepository(database_config.DATABASE_URL)
    repo.create_workspace("alice", "Alpha", workspace_id="alpha")
    repo.create_workspace("alice", "Beta", workspace_id="beta")
    reports = StrategyReportRepository(database_config.DATABASE_URL)
    reports.save_report("alice", report_id="alpha-report", strategy_name="trend", workspace_id="alpha")
    reports.save_report("alice", report_id="beta-report", strategy_name="trend", workspace_id="beta")

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/reports/db-list", params={"user_id": "alice", "workspace_id": "alpha"})
    items = response.json()["data"]["reports"]["items"]

    assert response.status_code == 200
    assert [item["report_id"] for item in items] == ["alpha-report"]
    assert all(item["workspace_id"] == "alpha" for item in items)


def test_production_blocks_non_member_workspace_access(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config
    from src.db.workspace_repository import WorkspaceRepository

    configure_env(monkeypatch, tmp_path, "production")
    repo = WorkspaceRepository(database_config.DATABASE_URL)
    repo.create_workspace("alice", "Alpha", workspace_id="alpha")
    repo.create_workspace("bob", "Beta", workspace_id="beta")
    client = TestClient(create_v2_api_app())
    login = client.post("/api/v2/auth/login", json={"user_id": "bob", "role": "admin"})
    session_id = login.json()["data"]["session"]["session_id"]

    response = client.get("/api/v2/reports/db-list", params={"workspace_id": "alpha"}, headers={"X-Session-ID": session_id})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "WORKSPACE_ACCESS_DENIED"


def test_workspace_audit_log_sanitizes_sensitive_metadata(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config
    from src.db.repository import AuditLogRepository

    configure_env(monkeypatch, tmp_path, "local")
    client = TestClient(create_v2_api_app())
    client.post(
        "/api/v2/workspaces",
        json={"workspace_id": "secret-team", "name": "Secret Team", "password": "hidden"},
        headers={"Authorization": "Bearer raw", "X-Session-ID": "raw-session", "X-API-Key": "raw-key"},
    )

    logs = AuditLogRepository(database_config.DATABASE_URL).list_logs_by_user("default")
    text = json.dumps(logs, ensure_ascii=False).lower()

    for forbidden in ["hidden", "raw-key", "raw-session", "bearer raw", "authorization", "password", "api_key", "session_id"]:
        assert forbidden not in text
    assert any(log["action"] == "workspace.create" for log in logs)


def test_workspace_source_keeps_safety_boundaries():
    import src.api.v2.auth as api_auth
    import src.api.v2.server as server
    import src.db.workspace_repository as workspace_repository
    import src.workspace.workspace_service as workspace_service

    combined = "\n".join(
        [
            inspect.getsource(api_auth),
            inspect.getsource(server),
            inspect.getsource(workspace_repository),
            inspect.getsource(workspace_service),
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto" + "order",
        "place_" + "order",
        "open" + "ai",
        "stripe_" + "secret",
        "password=",
        "token=",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in combined

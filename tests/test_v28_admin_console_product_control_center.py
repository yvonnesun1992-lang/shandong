from __future__ import annotations

import inspect
import json
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def configure_env(monkeypatch, tmp_path, auth_mode: str) -> str:
    from src.config import database_config

    db_url = sqlite_url(tmp_path / f"v28-{auth_mode}.db")
    monkeypatch.setenv("SHANDONG_AUTH_MODE", auth_mode)
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)
    return db_url


def assert_sanitized(payload: dict) -> None:
    text = json.dumps(payload, ensure_ascii=False).lower()
    for forbidden in [
        "secret",
        "token",
        "password",
        "api_key",
        "raw_key",
        "session_id",
        "authorization",
        ".env",
        "/users/apple",
        str(PROJECT_ROOT).lower(),
    ]:
        assert forbidden not in text


def test_build_admin_console_summary_returns_standard_structure(tmp_path, monkeypatch):
    from src.api.v2.admin_console import build_admin_console_summary

    configure_env(monkeypatch, tmp_path, "local")
    summary = build_admin_console_summary()

    assert set(summary) == {
        "system",
        "database",
        "security",
        "workspace",
        "billing",
        "deployment",
        "release_candidate",
        "warnings",
    }
    assert summary["system"]["status"] in {"ok", "warning"}
    assert summary["database"]["status"] in {"ok", "warning"}
    assert isinstance(summary["warnings"], list)
    assert_sanitized(summary)


def test_admin_console_endpoint_local_default_admin_access(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path, "local")
    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/admin/console")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "release_candidate" in response.json()["data"]["admin_console"]
    assert_sanitized(response.json())


def test_admin_console_production_requires_admin_session(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path, "production")
    client = TestClient(create_v2_api_app())

    anonymous = client.get("/api/v2/admin/console")
    assert anonymous.status_code in {401, 403}
    assert anonymous.json()["error"]["code"] in {"AUTH_REQUIRED", "PERMISSION_DENIED"}

    admin_login = client.post("/api/v2/auth/login", json={"user_id": "admin", "role": "admin"})
    admin_session = admin_login.json()["data"]["session"]["session_id"]
    admin_response = client.get("/api/v2/admin/console", headers={"X-Session-ID": admin_session})
    assert admin_response.status_code == 200
    assert admin_response.json()["success"] is True
    assert_sanitized(admin_response.json())

    viewer_login = client.post("/api/v2/auth/login", json={"user_id": "viewer", "role": "viewer"})
    viewer_session = viewer_login.json()["data"]["session"]["session_id"]
    viewer_response = client.get("/api/v2/admin/console", headers={"X-Session-ID": viewer_session})
    assert viewer_response.status_code == 403
    assert viewer_response.json()["error"]["code"] == "PERMISSION_DENIED"


def test_admin_console_submodule_exception_returns_warning(tmp_path, monkeypatch):
    import src.api.v2.admin_console as admin_console

    configure_env(monkeypatch, tmp_path, "local")

    def broken_database_health() -> dict:
        raise RuntimeError("database failed at /Users/apple/private/path/shandong_v2.db")

    monkeypatch.setattr(admin_console, "collect_database_health", broken_database_health)
    summary = admin_console.build_admin_console_summary()

    assert summary["database"]["status"] == "warning"
    assert summary["warnings"]
    assert_sanitized(summary)


def test_admin_console_frontend_and_docs_exist():
    frontend = PROJECT_ROOT / "web" / "frontend" / "app" / "admin" / "page.tsx"
    docs = PROJECT_ROOT / "docs" / "ADMIN_CONSOLE.md"

    assert frontend.exists()
    assert docs.exists()
    assert "Admin Console" in frontend.read_text(encoding="utf-8")
    assert "Admin Console" in docs.read_text(encoding="utf-8")


def test_v28_source_keeps_product_control_center_safety_boundaries():
    import src.api.v2.admin_console as admin_console

    source = "\n".join(
        [
            inspect.getsource(admin_console),
            (PROJECT_ROOT / "docs" / "ADMIN_CONSOLE.md").read_text(encoding="utf-8"),
            (PROJECT_ROOT / "web" / "frontend" / "app" / "admin" / "page.tsx").read_text(encoding="utf-8"),
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto" + "order",
        "place_" + "order",
        "open" + "ai",
        "stripe " + "live",
        "live_" + "secret",
        "password=",
        "token=",
        "api_key=",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in source

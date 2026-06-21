from __future__ import annotations

import importlib
import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_identity_planning_files_and_defaults(monkeypatch):
    assert (ROOT / "src/config/identity_config.py").exists()
    assert (ROOT / "src/auth/identity_provider.py").exists()

    monkeypatch.delenv("SHANDONG_IDENTITY_MODE", raising=False)
    monkeypatch.delenv("SHANDONG_IDENTITY_PROVIDER", raising=False)
    identity_config = importlib.import_module("src.config.identity_config")
    identity_config = importlib.reload(identity_config)

    assert identity_config.identity_mode() == "demo"
    assert identity_config.identity_provider() == "demo"


def test_production_identity_does_not_enable_real_provider(monkeypatch):
    monkeypatch.setenv("SHANDONG_IDENTITY_MODE", "production")
    monkeypatch.delenv("SHANDONG_IDENTITY_PROVIDER", raising=False)
    identity_config = importlib.import_module("src.config.identity_config")
    identity_config = importlib.reload(identity_config)

    status = identity_config.identity_planning_status()

    assert status["mode"] == "production"
    assert status["provider"] == "demo"
    assert status["production_ready"] is False
    assert status["external_provider_enabled"] is False


def test_identity_plan_endpoint_is_public_and_sanitized(monkeypatch):
    monkeypatch.delenv("SHANDONG_IDENTITY_MODE", raising=False)
    monkeypatch.delenv("SHANDONG_IDENTITY_PROVIDER", raising=False)
    monkeypatch.setenv("SHANDONG_AUTH_MODE", "production")
    monkeypatch.setenv("SHANDONG_REQUIRE_AUTH", "true")
    monkeypatch.setenv("SHANDONG_ALLOW_LOCAL_ADMIN_FALLBACK", "false")

    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/identity-plan")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["identity"]["mode"] == "demo"
    assert payload["data"]["identity"]["provider"] == "demo"
    assert payload["data"]["identity"]["production_ready"] is False
    assert payload["data"]["identity"]["external_provider_enabled"] is False

    lowered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in ["secret", "token", "password", "api_key", "client_secret", "client_id"]:
        assert forbidden not in lowered


def test_frontend_login_and_admin_show_identity_boundary():
    login_page = read_text("web/frontend/app/login/page.tsx")
    admin_page = read_text("web/frontend/app/admin/page.tsx")
    identity_status = read_text("web/frontend/app/lib/identityStatus.ts")

    assert "Demo login only" in login_page
    assert "Not production identity" in login_page
    assert "No OAuth connected" in login_page
    assert "No password stored" in login_page
    assert "No external provider connected" in login_page
    assert "Google Login" not in login_page
    assert "GitHub Login" not in login_page
    assert "OAuth button" not in login_page

    assert "Identity Provider" in admin_page
    assert "Production identity: planned" in admin_page
    assert "External provider: not connected" in admin_page
    assert "OAuth: not connected" in admin_page
    assert "Password storage: none" in admin_page

    assert "getIdentityMode" in identity_status
    assert "getIdentityProviderLabel" in identity_status
    assert "getIdentityBoundaryNotice" in identity_status


def test_identity_plan_docs_and_review_package_exist():
    docs = read_text("docs/PRODUCTION_IDENTITY_PLAN.md")
    readme = read_text("README.md")
    review = read_text("REVIEW_PACKAGE.md")

    assert "Current State" in docs
    assert "Future Options" in docs
    assert "Not Implemented Yet" in docs
    assert "No OAuth implemented" in docs
    assert "No production identity provider enabled" in docs
    assert "V3.3" in readme
    assert "Production Identity Provider Planning" in readme
    assert "V3.3" in review
    assert "production identity system planning" in review.lower()


def test_v33_runtime_boundaries():
    runtime_files = [
        "src/config/identity_config.py",
        "src/auth/identity_provider.py",
        "src/api/v2/server.py",
        "web/frontend/app/lib/identityStatus.ts",
        "web/frontend/app/login/page.tsx",
        "web/frontend/app/admin/page.tsx",
    ]
    combined = "\n".join(read_text(path) for path in runtime_files).lower()

    forbidden = [
        "broker api",
        "auto order",
        "place_order",
        "openai",
        "stripe live",
        "real oauth",
        "production secret",
        "password=",
        "token=",
        "api_key=",
        "client_secret",
        "client_id",
        "sk-",
        "eval(",
        "exec(",
    ]
    for pattern in forbidden:
        assert pattern not in combined

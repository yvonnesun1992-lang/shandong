from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_production_identity_modules_exist_and_default_safe(monkeypatch):
    monkeypatch.delenv("SHANDONG_PRODUCTION_IDENTITY_MODE", raising=False)
    monkeypatch.delenv("SHANDONG_PRODUCTION_IDENTITY_PROVIDER", raising=False)
    monkeypatch.delenv("SHANDONG_ENABLE_PRODUCTION_IDENTITY", raising=False)
    monkeypatch.delenv("SHANDONG_EXTERNAL_IDENTITY_MAPPING_READY", raising=False)
    monkeypatch.delenv("SHANDONG_PRODUCTION_SESSION_LIFECYCLE_READY", raising=False)

    from src.auth.production_identity_plan import get_production_identity_integration_plan, validate_identity_integration_boundary
    from src.config.production_identity_config import production_identity_enabled, production_identity_mode

    assert (ROOT / "src/config/production_identity_config.py").exists()
    assert (ROOT / "src/auth/production_identity_plan.py").exists()
    assert (ROOT / "scripts/production_identity_integration_check.py").exists()
    assert production_identity_mode() == "demo"
    assert production_identity_enabled() is False

    plan = get_production_identity_integration_plan()
    boundary = validate_identity_integration_boundary()
    assert plan["current_identity"] == "demo_auth"
    assert plan["future_identity"] == "external_oidc_planned"
    assert plan["production_identity_enabled"] is False
    assert plan["external_identity_connected"] is False
    assert boundary["valid"] is True


def test_identity_integration_endpoint_is_sanitized():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/identity-integration")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    identity = payload["data"]["identity_integration"]
    assert identity["current_identity"] == "demo_auth"
    assert identity["future_identity"] == "external_oidc_planned"
    assert identity["production_identity_enabled"] is False
    assert identity["external_identity_connected"] is False
    assert identity["external_identity_mapping_ready"] is False
    assert identity["production_session_lifecycle_ready"] is False
    assert identity["auth_audit_ready"] == "planned"

    lowered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in ["client_id", "client_secret", "access_token", "refresh_token", "password", "secret", "api_key", "session_id", "authorization", "/users/apple"]:
        assert forbidden not in lowered


def test_production_identity_integration_check_returns_not_ready():
    from scripts.production_identity_integration_check import run_production_identity_integration_check

    result = run_production_identity_integration_check()
    assert result["success"] is True
    assert result["production_identity_ready"] is False
    assert isinstance(result["checks"], list)
    assert result["errors"] == []


def test_frontend_admin_docs_and_package_updates_exist():
    api_client = read_text("web/frontend/app/lib/apiClient.ts")
    admin_page = read_text("web/frontend/app/admin/page.tsx")
    docs = read_text("docs/PRODUCTION_IDENTITY_INTEGRATION_PLAN.md")
    readiness_doc = read_text("docs/V4_PRODUCTION_LAUNCH_READINESS.md")
    readme = read_text("README.md")
    review = read_text("REVIEW_PACKAGE.md")

    assert "fetchIdentityIntegration" in api_client
    assert "/api/v2/system/identity-integration" in api_client
    assert "Production Identity Integration" in admin_page
    assert "Current identity: demo auth" in admin_page
    assert "Future identity: external OIDC planned" in admin_page
    assert "Production identity: not connected" in admin_page
    assert "External mapping: not ready" in admin_page
    assert "Session lifecycle: planned" in admin_page
    assert "Auth audit: planned" in admin_page

    for phrase in [
        "Current State",
        "Why Identity Integration Matters",
        "Recommended Future Architecture",
        "Identity Mapping Checklist",
        "Session Lifecycle Checklist",
        "Not Implemented Yet",
        "No production identity provider connected",
        "No OAuth implemented",
        "No Google Login",
        "No GitHub Login",
        "No client_id",
        "No client_secret",
        "No access token",
        "No refresh token",
    ]:
        assert phrase in docs

    assert "V4.2" in readiness_doc
    assert "production identity integration is planned" in readiness_doc
    assert "production_identity_ready remains false" in readiness_doc
    assert "V4.2" in readme
    assert "Production Identity Integration Plan" in readme
    assert "Identity integration endpoint" in readme
    assert "No real identity provider connected" in readme
    assert "V4.2" in review
    assert "生产身份集成规划" in review


def test_v42_runtime_boundaries():
    runtime_files = [
        "src/config/production_identity_config.py",
        "src/auth/production_identity_plan.py",
        "scripts/production_identity_integration_check.py",
        "src/api/v2/server.py",
        "web/frontend/app/admin/page.tsx",
        "web/frontend/app/lib/apiClient.ts",
    ]
    combined = "\n".join(read_text(path) for path in runtime_files).lower()

    forbidden = [
        "client_id=",
        "client_secret",
        "access_token",
        "refresh_token",
        "auth0",
        "clerk",
        "firebase auth",
        "supabase auth",
        "broker api",
        "auto order",
        "place_order",
        "openai",
        "production secret",
        "password=",
        "token=",
        "api_key=",
        "eval(",
        "exec(",
    ]
    for pattern in forbidden:
        assert pattern not in combined

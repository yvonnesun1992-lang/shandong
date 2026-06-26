from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_deployment_target_modules_exist_and_default_safe(monkeypatch):
    monkeypatch.delenv("SHANDONG_DEPLOYMENT_TARGET_MODE", raising=False)
    monkeypatch.delenv("SHANDONG_FRONTEND_TARGET", raising=False)
    monkeypatch.delenv("SHANDONG_BACKEND_TARGET", raising=False)
    monkeypatch.delenv("SHANDONG_DATABASE_TARGET", raising=False)
    monkeypatch.delenv("SHANDONG_SECRETS_TARGET", raising=False)
    monkeypatch.delenv("SHANDONG_MONITORING_TARGET", raising=False)

    from src.config.deployment_target_config import deployment_target_mode
    from src.deployment.deployment_target_plan import get_deployment_target_plan, validate_deployment_target_boundary

    assert (ROOT / "src/config/deployment_target_config.py").exists()
    assert (ROOT / "src/deployment/deployment_target_plan.py").exists()
    assert (ROOT / "scripts/deployment_target_selection_check.py").exists()
    assert deployment_target_mode() == "local"

    plan = get_deployment_target_plan()
    boundary = validate_deployment_target_boundary()
    assert plan["current_state"] == "local_demo"
    assert plan["frontend_target"] == "vercel_planned"
    assert plan["backend_target"] == "render_or_flyio_planned"
    assert plan["database_target"] == "postgres_planned"
    assert plan["production_deployment_enabled"] is False
    assert boundary["valid"] is True


def test_deployment_target_endpoint_is_sanitized():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/deployment-target")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    target = payload["data"]["deployment_target"]
    assert target["current_state"] == "local_demo"
    assert target["frontend_target"] == "vercel_planned"
    assert target["backend_target"] == "render_or_flyio_planned"
    assert target["production_deployment_enabled"] is False
    assert target["external_cloud_connected"] is False

    lowered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in ["cloud key", "token=", "password", "api_key", "database_url", "/users/apple", "authorization"]:
        assert forbidden not in lowered


def test_deployment_target_selection_check_returns_not_ready():
    from scripts.deployment_target_selection_check import run_deployment_target_selection_check

    result = run_deployment_target_selection_check()
    assert result["success"] is True
    assert result["production_deployment_ready"] is False
    assert isinstance(result["checks"], list)
    assert result["errors"] == []


def test_frontend_admin_docs_and_package_updates_exist():
    api_client = read_text("web/frontend/app/lib/apiClient.ts")
    admin_page = read_text("web/frontend/app/admin/page.tsx")
    docs = read_text("docs/PRODUCTION_DEPLOYMENT_TARGET_SELECTION.md")
    readiness_doc = read_text("docs/V4_PRODUCTION_LAUNCH_READINESS.md")
    readme = read_text("README.md")
    review = read_text("REVIEW_PACKAGE.md")

    assert "fetchDeploymentTarget" in api_client
    assert "/api/v2/system/deployment-target" in api_client
    assert "Production Deployment Target" in admin_page
    assert "Current state: local demo" in admin_page
    assert "Frontend: Vercel planned" in admin_page
    assert "Backend: Render / Fly.io planned" in admin_page
    assert "Database: PostgreSQL planned" in admin_page
    assert "Secrets: managed secrets planned" in admin_page
    assert "Monitoring: Sentry / OpenTelemetry planned" in admin_page
    assert "Production deployment: not enabled" in admin_page

    for phrase in [
        "Current State",
        "Candidate Targets",
        "Frontend",
        "Backend",
        "Database",
        "Secrets",
        "Monitoring",
        "Recommended First Deployment Stack",
        "Decision Criteria",
        "Not Implemented Yet",
        "No production deployment",
        "No cloud provider connected",
        "No production token",
        "No DATABASE_URL",
        "No domain",
        "No TLS",
        "No external log upload",
        "No real payment",
        "No broker connection",
        "No auto trading",
    ]:
        assert phrase in docs

    assert "V4.3" in readiness_doc
    assert "production deployment target selection is planned" in readiness_doc
    assert "external cloud remains not connected" in readiness_doc
    assert "V4.3" in readme
    assert "Production Deployment Target Selection" in readme
    assert "No production deployment enabled" in readme
    assert "V4.3" in review
    assert "生产部署目标选择规划" in review


def test_v43_runtime_boundaries():
    runtime_files = [
        "src/config/deployment_target_config.py",
        "src/deployment/deployment_target_plan.py",
        "scripts/deployment_target_selection_check.py",
        "src/api/v2/server.py",
        "web/frontend/app/admin/page.tsx",
        "web/frontend/app/lib/apiClient.ts",
    ]
    combined = "\n".join(read_text(path) for path in runtime_files).lower()

    forbidden = [
        "vercel_token",
        "render_api",
        "railway_token",
        "flyio_token",
        "aws_access_key",
        "gcp_service_account",
        "azure_client",
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

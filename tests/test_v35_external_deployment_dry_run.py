from __future__ import annotations

import importlib
import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_deployment_config_defaults(monkeypatch):
    assert (ROOT / "src/config/deployment_config.py").exists()
    monkeypatch.delenv("SHANDONG_DEPLOYMENT_MODE", raising=False)
    monkeypatch.delenv("SHANDONG_DEPLOYMENT_TARGET", raising=False)
    config = importlib.import_module("src.config.deployment_config")
    config = importlib.reload(config)

    assert config.deployment_mode() == "local"
    assert config.deployment_target() == "local"
    assert config.dry_run_enabled() is True
    assert config.external_deployment_enabled() is False


def test_deployment_dry_run_check_returns_success_structure():
    assert (ROOT / "scripts/deployment_dry_run_check.py").exists()
    module = importlib.import_module("scripts.deployment_dry_run_check")
    result = module.run_deployment_dry_run_check()

    assert set(result) == {"success", "checks", "warnings", "errors"}
    assert isinstance(result["success"], bool)
    assert isinstance(result["checks"], list)
    assert isinstance(result["warnings"], list)
    assert isinstance(result["errors"], list)


def test_deployment_dry_run_endpoint_is_sanitized(monkeypatch):
    monkeypatch.delenv("SHANDONG_DEPLOYMENT_MODE", raising=False)
    monkeypatch.delenv("SHANDONG_DEPLOYMENT_TARGET", raising=False)

    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/deployment-dry-run")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    deployment = payload["data"]["deployment"]
    assert deployment["mode"] == "local"
    assert deployment["target"] == "local"
    assert deployment["dry_run_enabled"] is True
    assert deployment["external_deployment_enabled"] is False
    assert deployment["checks_available"] is True

    lowered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in ["secret", "token", "password", "api_key", "database_url", "cloud key", "/users/apple"]:
        assert forbidden not in lowered


def test_frontend_admin_and_docs_surface_deployment_dry_run():
    api_client = read_text("web/frontend/app/lib/apiClient.ts")
    admin_page = read_text("web/frontend/app/admin/page.tsx")
    dry_run_doc = read_text("docs/EXTERNAL_DEPLOYMENT_DRY_RUN.md")
    deployment_doc = read_text("docs/DEPLOYMENT.md")
    runbook = read_text("docs/OPERATIONS_RUNBOOK.md")

    assert "fetchDeploymentDryRun" in api_client
    assert "/api/v2/system/deployment-dry-run" in api_client
    assert "Deployment Dry Run" in admin_page
    assert "Deployment mode: local" in admin_page
    assert "External deployment: not connected" in admin_page
    assert "Dry run check: available" in admin_page
    assert "Production launch: not enabled" in admin_page

    assert "Current State" in dry_run_doc
    assert "Dry Run Goals" in dry_run_doc
    assert "No production deployment" in dry_run_doc
    assert "No cloud provider connected" in dry_run_doc
    assert "dry run" in deployment_doc.lower()
    assert "deployment_dry_run_check.py" in deployment_doc
    assert "dry run" in runbook.lower()
    assert "deployment_dry_run_check.py" in runbook


def test_readme_and_review_package_mention_v35():
    readme = read_text("README.md")
    review = read_text("REVIEW_PACKAGE.md")

    assert "V3.5" in readme
    assert "External Deployment Dry Run" in readme
    assert "Deployment dry run endpoint" in readme
    assert "No production cloud connected" in readme
    assert "V3.5" in review
    assert "外部部署演练" in review or "external deployment dry run" in review.lower()


def test_v35_runtime_boundaries():
    runtime_files = [
        "src/config/deployment_config.py",
        "scripts/deployment_dry_run_check.py",
        "src/api/v2/server.py",
        "web/frontend/app/admin/page.tsx",
    ]
    combined = "\n".join(read_text(path) for path in runtime_files).lower()

    forbidden = [
        "aws_access_key",
        "google_application_credentials",
        "azure_client",
        "vercel_token",
        "render_api",
        "railway_token",
        "real database",
        "broker api",
        "auto order",
        "place_order",
        "openai",
        "stripe live",
        "production secret",
        "eval(",
        "exec(",
    ]
    for pattern in forbidden:
        assert pattern not in combined
    assert not (ROOT / ".env").exists()

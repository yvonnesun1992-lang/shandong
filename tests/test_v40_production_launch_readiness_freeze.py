from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_production_launch_readiness_check_exists_and_returns_freeze_status():
    from scripts.production_launch_readiness_check import run_production_launch_readiness_check

    script = ROOT / "scripts/production_launch_readiness_check.py"
    assert script.exists()

    result = run_production_launch_readiness_check()
    assert set(result) >= {"success", "checks", "warnings", "errors", "production_ready", "demo_ready"}
    assert result["success"] is True
    assert result["production_ready"] is False
    assert result["demo_ready"] is True
    assert isinstance(result["checks"], list)
    assert isinstance(result["warnings"], list)
    assert isinstance(result["errors"], list)

    lowered = json.dumps(result, sort_keys=True).lower()
    for forbidden in ["secret", "token", "password", "api_key", "session_id", "authorization", "/users/apple", "aws_access_key"]:
        assert forbidden not in lowered


def test_production_readiness_endpoint_is_sanitized():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/production-readiness")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    readiness = payload["data"]["production_readiness"]
    assert readiness["version"] == "V4.0"
    assert readiness["demo_ready"] is True
    assert readiness["production_ready"] is False
    assert readiness["external_services_connected"] is False
    assert readiness["broker_connected"] is False
    assert readiness["real_payment_enabled"] is False
    assert readiness["production_identity_enabled"] is False
    assert "production identity provider not connected" in readiness["blocking_items"]

    lowered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in ["secret", "token", "password", "api_key", "session_id", "authorization", "cloud key", "/users/apple"]:
        assert forbidden not in lowered


def test_frontend_api_and_admin_production_readiness_surface():
    api_client = read_text("web/frontend/app/lib/apiClient.ts")
    admin_page = read_text("web/frontend/app/admin/page.tsx")

    assert "fetchProductionReadiness" in api_client
    assert "/api/v2/system/production-readiness" in api_client
    assert "Production Launch Readiness" in admin_page
    assert "Demo ready: yes" in admin_page
    assert "Production ready: no" in admin_page
    assert "Production identity: not connected" in admin_page
    assert "Production database: not connected" in admin_page
    assert "Cloud deployment: not connected" in admin_page
    assert "Real payment: not enabled" in admin_page
    assert "Broker integration: intentionally disabled" in admin_page
    assert "Legal/compliance: pending" in admin_page


def test_v4_launch_readiness_docs_and_package_updates_exist():
    docs = read_text("docs/V4_PRODUCTION_LAUNCH_READINESS.md")
    readme = read_text("README.md")
    review = read_text("REVIEW_PACKAGE.md")

    for phrase in [
        "Current V4 Status",
        "Demo-ready",
        "Not production-ready",
        "Ready Items",
        "Blocking Items Before Real Launch",
        "V4 Roadmap",
        "Not Implemented Yet",
        "No production launch",
        "No production cloud",
        "No production database",
        "No production identity",
        "No real payment",
        "No broker connection",
        "No auto trading",
        "No external AI API",
    ]:
        assert phrase in docs

    assert "V4.0" in readme
    assert "Production Launch Readiness Freeze" in readme
    assert "Demo-ready but not production-ready" in readme
    assert "Production readiness endpoint" in readme
    assert "No production launch" in readme
    assert "V4.0" in review
    assert "production launch readiness freeze" in review.lower()


def test_v40_runtime_boundaries():
    runtime_files = [
        "scripts/production_launch_readiness_check.py",
        "src/api/v2/server.py",
        "web/frontend/app/admin/page.tsx",
        "web/frontend/app/lib/apiClient.ts",
    ]
    combined = "\n".join(read_text(path) for path in runtime_files).lower()

    forbidden = [
        ".env committed",
        "aws_access_key",
        "google_application_credentials",
        "azure_client",
        "real database url",
        "broker api",
        "auto order",
        "place_order",
        "openai",
        "oauth client",
        "production secret",
        "eval(",
        "exec(",
    ]
    for pattern in forbidden:
        assert pattern not in combined

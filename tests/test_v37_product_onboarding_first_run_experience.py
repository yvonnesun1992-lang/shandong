from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_onboarding_page_and_first_run_checklist_exist():
    onboarding_page = ROOT / "web/frontend/app/onboarding/page.tsx"
    checklist = ROOT / "web/frontend/app/components/FirstRunChecklist.tsx"

    assert onboarding_page.exists()
    assert checklist.exists()

    page_text = onboarding_page.read_text(encoding="utf-8")
    checklist_text = checklist.read_text(encoding="utf-8")

    assert "Welcome to Shandong" in page_text
    assert "Research mode only" in page_text
    assert "No broker connection" in page_text
    assert "No auto trading" in page_text
    assert "No real payment" in page_text
    assert "No production identity" in page_text
    assert "No external cloud connected" in page_text
    assert "No AI API connected" in page_text
    assert "Demo / local mode" in page_text
    assert "Open Dashboard" in page_text
    assert "Demo Login" in page_text
    assert "Admin Console" in page_text
    assert "API Docs" in page_text

    for item in [
        "Backend health ready",
        "Frontend shell ready",
        "Demo login available",
        "Admin Console available",
        "Observability local only",
        "Deployment dry run only",
        "V3 release candidate ready",
        "Safety boundaries visible",
    ]:
        assert item in checklist_text


def test_onboarding_endpoint_is_sanitized():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/onboarding")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    onboarding = payload["data"]["onboarding"]
    assert onboarding["version"] == "V3.7"
    assert onboarding["mode"] == "demo"
    assert onboarding["first_run_ready"] is True
    assert onboarding["external_services_connected"] is False
    assert onboarding["recommended_steps"]
    assert onboarding["safety_boundaries"]

    lowered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in ["secret", "token", "password", "api_key", "session_id", "authorization", "cloud key", "/users/apple"]:
        assert forbidden not in lowered


def test_frontend_api_nav_and_admin_onboarding_surface():
    api_client = read_text("web/frontend/app/lib/apiClient.ts")
    shell = read_text("web/frontend/app/components/ProductionShell.tsx")
    admin_page = read_text("web/frontend/app/admin/page.tsx")

    assert "fetchOnboarding" in api_client
    assert "/api/v2/system/onboarding" in api_client
    assert "Onboarding" in shell
    assert "/onboarding" in shell
    assert "Dashboard" in shell
    assert "Admin Console" in shell
    assert "API Docs" in shell
    assert "Onboarding Readiness" in admin_page
    assert "First-run ready: yes" in admin_page
    assert "Demo journey: available" in admin_page
    assert "Safety boundaries: visible" in admin_page
    assert "External services: not connected" in admin_page
    assert "Production launch: not enabled" in admin_page


def test_product_onboarding_docs_and_package_updates_exist():
    docs = read_text("docs/PRODUCT_ONBOARDING.md")
    readme = read_text("README.md")
    review = read_text("REVIEW_PACKAGE.md")

    assert "Product Positioning" in docs
    assert "First-Run Experience" in docs
    assert "What Users Can Do" in docs
    assert "What Users Cannot Do" in docs
    assert "Demo Script" in docs
    assert "Cannot place trades" in docs
    assert "Cannot connect broker" in docs
    assert "V3.7" in readme
    assert "Product Onboarding" in readme
    assert "First-Run Experience" in readme
    assert "Onboarding endpoint" in readme
    assert "V3.7" in review
    assert "产品 onboarding" in review or "product onboarding" in review.lower()


def test_v37_runtime_boundaries():
    runtime_files = [
        "src/api/v2/server.py",
        "web/frontend/app/onboarding/page.tsx",
        "web/frontend/app/components/FirstRunChecklist.tsx",
        "web/frontend/app/components/ProductionShell.tsx",
        "web/frontend/app/admin/page.tsx",
        "web/frontend/app/lib/apiClient.ts",
    ]
    combined = "\n".join(read_text(path) for path in runtime_files).lower()

    forbidden = [
        "broker api",
        "auto order",
        "place_order",
        "openai",
        "stripe live",
        "oauth client",
        "production secret",
        "eval(",
        "exec(",
    ]
    for pattern in forbidden:
        assert pattern not in combined

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_workspace_demo_page_and_card_exist():
    page = ROOT / "web/frontend/app/workspace-demo/page.tsx"
    card = ROOT / "web/frontend/app/components/WorkspaceDemoCard.tsx"

    assert page.exists()
    assert card.exists()

    page_text = page.read_text(encoding="utf-8")
    card_text = card.read_text(encoding="utf-8")

    for phrase in [
        "Demo Workspace Overview",
        "Workspace member roles",
        "Quota snapshot",
        "Usage summary",
        "Research reports overview",
        "Safety boundaries",
        "Next actions",
        "Demo workspace only",
        "No real customer connected",
        "No real billing",
        "No broker connection",
        "No auto trading",
    ]:
        assert phrase in page_text

    for phrase in ["Workspace name", "Plan", "Role", "Quota", "Usage", "Reports", "Status"]:
        assert phrase in card_text


def test_workspace_demo_endpoint_is_sanitized():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/workspace-demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    workspace_demo = payload["data"]["workspace_demo"]
    assert workspace_demo["workspace_name"] == "Demo Workspace"
    assert workspace_demo["plan"] == "demo"
    assert workspace_demo["roles"] == ["admin", "user", "viewer"]
    assert workspace_demo["real_customer_connected"] is False
    assert workspace_demo["real_billing_enabled"] is False
    assert workspace_demo["broker_connected"] is False
    assert workspace_demo["auto_trading_enabled"] is False

    lowered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in ["secret", "token", "password", "api_key", "session_id", "payment", "authorization", "/users/apple"]:
        assert forbidden not in lowered


def test_frontend_api_nav_and_admin_workspace_demo_surface():
    api_client = read_text("web/frontend/app/lib/apiClient.ts")
    shell = read_text("web/frontend/app/components/ProductionShell.tsx")
    admin_page = read_text("web/frontend/app/admin/page.tsx")

    assert "fetchWorkspaceDemo" in api_client
    assert "/api/v2/system/workspace-demo" in api_client
    assert "Workspace Demo" in shell
    assert "/workspace-demo" in shell
    assert "Workspace Demo" in admin_page
    assert "Demo workspace: available" in admin_page
    assert "Roles: admin / user / viewer" in admin_page
    assert "Quota: demo only" in admin_page
    assert "Billing: mock" in admin_page
    assert "Real customer: not connected" in admin_page
    assert "Broker: not connected" in admin_page


def test_workspace_demo_docs_and_package_updates_exist():
    docs = read_text("docs/WORKSPACE_DEMO_FLOW.md")
    readme = read_text("README.md")
    review = read_text("REVIEW_PACKAGE.md")

    assert "Workspace Concept" in docs
    assert "Demo Workspace Flow" in docs
    assert "What Is Demo Only" in docs
    assert "Not Implemented Yet" in docs
    assert "real customer onboarding" in docs
    assert "real billing" in docs
    assert "V3.8" in readme
    assert "Customer Workspace Demo Flow" in readme
    assert "Workspace Demo endpoint" in readme
    assert "No real customer connected" in readme
    assert "V3.8" in review
    assert "customer workspace demo flow" in review.lower()


def test_v38_runtime_boundaries():
    runtime_files = [
        "src/api/v2/server.py",
        "web/frontend/app/workspace-demo/page.tsx",
        "web/frontend/app/components/WorkspaceDemoCard.tsx",
        "web/frontend/app/components/ProductionShell.tsx",
        "web/frontend/app/admin/page.tsx",
        "web/frontend/app/lib/apiClient.ts",
    ]
    combined = "\n".join(read_text(path) for path in runtime_files).lower()

    forbidden = [
        "real customer account",
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

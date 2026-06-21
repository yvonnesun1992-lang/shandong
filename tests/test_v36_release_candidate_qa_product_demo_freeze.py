from __future__ import annotations

import importlib
import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v3_release_candidate_check_returns_success_structure():
    assert (ROOT / "scripts/v3_release_candidate_check.py").exists()
    module = importlib.import_module("scripts.v3_release_candidate_check")
    result = module.run_v3_release_candidate_check()

    assert set(result) == {"success", "checks", "warnings", "errors"}
    assert isinstance(result["success"], bool)
    assert isinstance(result["checks"], list)
    assert isinstance(result["warnings"], list)
    assert isinstance(result["errors"], list)


def test_v3_release_candidate_endpoint_is_sanitized():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/v3-release-candidate")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    release_candidate = payload["data"]["release_candidate"]
    assert release_candidate["version"] == "V3.6"
    assert release_candidate["scope"] == "product_demo_freeze"
    assert release_candidate["demo_ready"] is True
    assert release_candidate["external_services_connected"] is False
    assert release_candidate["broker_connected"] is False
    assert release_candidate["real_payment_enabled"] is False
    assert release_candidate["production_identity_enabled"] is False

    lowered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in ["secret", "token", "password", "api_key", "session_id", "authorization", "cloud key", "/users/apple"]:
        assert forbidden not in lowered


def test_frontend_admin_and_api_client_surface_v36_freeze():
    api_client = read_text("web/frontend/app/lib/apiClient.ts")
    admin_page = read_text("web/frontend/app/admin/page.tsx")

    assert "fetchV3ReleaseCandidate" in api_client
    assert "/api/v2/system/v3-release-candidate" in api_client
    assert "Release Candidate Freeze" in admin_page
    assert "Version: V3.6" in admin_page
    assert "Demo ready: yes" in admin_page
    assert "External services: not connected" in admin_page
    assert "Broker: not connected" in admin_page
    assert "Real payment: not enabled" in admin_page
    assert "Production identity: not enabled" in admin_page
    assert "Deployment: dry run only" in admin_page


def test_v3_product_demo_freeze_docs_and_existing_docs_are_updated():
    freeze_doc = read_text("docs/V3_PRODUCT_DEMO_FREEZE.md")
    local_demo = read_text("docs/LOCAL_DEMO_GUIDE.md")
    operations = read_text("docs/OPERATIONS_RUNBOOK.md")
    external_deployment = read_text("docs/EXTERNAL_DEPLOYMENT_DRY_RUN.md")

    assert "V3 Release Candidate Scope" in freeze_doc
    assert "Demo Flow" in freeze_doc
    assert "Demo Safety Boundaries" in freeze_doc
    assert "Known Limitations" in freeze_doc
    assert "Release Candidate Checklist" in freeze_doc
    assert "No broker connection" in freeze_doc
    assert "No production cloud connected" in freeze_doc
    assert "V3.6" in local_demo
    assert "v3_release_candidate_check.py" in local_demo
    assert "V3.6" in operations
    assert "v3_release_candidate_check.py" in operations
    assert "V3.6" in external_deployment
    assert "not a production launch" in external_deployment.lower()


def test_readme_and_review_package_mention_v36():
    readme = read_text("README.md")
    review = read_text("REVIEW_PACKAGE.md")

    assert "V3.6" in readme
    assert "Release Candidate QA" in readme
    assert "Product Demo Freeze" in readme
    assert "V3 release candidate endpoint" in readme
    assert "No production launch" in readme
    assert "V3.6" in review
    assert "product demo freeze" in review.lower() or "产品演示冻结" in review


def test_v36_runtime_boundaries():
    runtime_files = [
        "scripts/v3_release_candidate_check.py",
        "src/api/v2/server.py",
        "web/frontend/app/admin/page.tsx",
        "web/frontend/app/lib/apiClient.ts",
    ]
    combined = "\n".join(read_text(path) for path in runtime_files).lower()

    forbidden = [
        "aws_access_key",
        "google_application_credentials",
        "azure_client",
        "vercel_token",
        "real database",
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
    assert not (ROOT / ".env").exists()

from __future__ import annotations

import inspect
import json
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def configure_env(monkeypatch, tmp_path) -> str:
    from src.config import database_config

    db_url = sqlite_url(tmp_path / "v29-local.db")
    monkeypatch.setenv("SHANDONG_AUTH_MODE", "local")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)
    return db_url


def assert_no_sensitive_output(payload: dict) -> None:
    text = json.dumps(payload, ensure_ascii=False).lower()
    for forbidden in [
        "secret",
        "token",
        "password",
        "api_key",
        "session_id",
        "authorization",
        "raw_key",
        ".env",
        "/users/apple",
        str(PROJECT_ROOT).lower(),
    ]:
        assert forbidden not in text


def test_local_startup_verification_returns_success_structure(tmp_path, monkeypatch):
    from scripts.local_startup_verification import run_local_startup_verification

    configure_env(monkeypatch, tmp_path)
    result = run_local_startup_verification()

    assert set(result) == {"success", "checks", "warnings", "errors"}
    assert result["success"] is True
    assert isinstance(result["checks"], list)
    assert len(result["checks"]) >= 20
    assert_no_sensitive_output(result)


def test_local_startup_api_health_endpoints_are_accessible(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path)
    client = TestClient(create_v2_api_app())

    for endpoint in [
        "/api/v2/admin/console",
        "/api/v2/system/liveness",
        "/api/v2/system/readiness",
        "/api/v2/system/security-health",
        "/api/v2/system/billing-health",
        "/api/v2/system/workspace-health",
    ]:
        response = client.get(endpoint)
        assert response.status_code == 200
        assert response.json()["success"] is True


def test_v29_review_and_demo_docs_exist():
    architecture_review = PROJECT_ROOT / "docs" / "V2_ARCHITECTURE_REVIEW.md"
    local_demo = PROJECT_ROOT / "docs" / "LOCAL_DEMO_GUIDE.md"

    assert architecture_review.exists()
    assert local_demo.exists()
    assert "Current V2 Architecture" in architecture_review.read_text(encoding="utf-8")
    assert "How to run local backend" in local_demo.read_text(encoding="utf-8")


def test_v29_readme_and_review_package_are_updated():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    review = (PROJECT_ROOT / "REVIEW_PACKAGE.md").read_text(encoding="utf-8")

    assert "V2.9" in readme
    assert "Architecture Review" in readme
    assert "Local Startup Verification" in readme
    assert "V2.9" in review
    assert "local_startup_verification" in review


def test_v29_source_keeps_safety_boundaries():
    import scripts.local_startup_verification as local_startup_verification

    source = "\n".join(
        [
            inspect.getsource(local_startup_verification),
            (PROJECT_ROOT / "docs" / "V2_ARCHITECTURE_REVIEW.md").read_text(encoding="utf-8"),
            (PROJECT_ROOT / "docs" / "LOCAL_DEMO_GUIDE.md").read_text(encoding="utf-8"),
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

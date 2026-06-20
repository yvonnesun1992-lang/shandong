from __future__ import annotations

import inspect
import json
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_env_example_exists_and_contains_only_placeholders():
    env_example = PROJECT_ROOT / ".env.example"
    text = env_example.read_text(encoding="utf-8")

    assert "SHANDONG_AUTH_MODE=local" in text
    assert "SHANDONG_DATABASE_URL=sqlite:///data/shandong_v2.db" in text
    assert "production" in text.lower()
    for forbidden in ["sk-", "ghp_", "xoxb-", "-----BEGIN", "real_secret", "live_secret"]:
        assert forbidden not in text


def test_startup_check_returns_success_structure(tmp_path, monkeypatch):
    from scripts.startup_check import run_startup_check
    from src.config import database_config

    monkeypatch.setattr(database_config, "DATABASE_URL", f"sqlite:///{(tmp_path / 'ops.db').as_posix()}")
    result = run_startup_check()

    assert set(result) == {"success", "checks", "warnings", "errors"}
    assert isinstance(result["checks"], list)
    assert result["success"] is True


def test_liveness_does_not_require_database(monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config

    monkeypatch.setattr(database_config, "DATABASE_URL", "postgresql://not-enabled")
    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/liveness")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "alive"


def test_readiness_returns_standard_response(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config

    monkeypatch.setattr(database_config, "DATABASE_URL", f"sqlite:///{(tmp_path / 'ready.db').as_posix()}")
    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/readiness")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "readiness" in response.json()["data"]
    assert isinstance(response.json()["warning"], list)


def test_docker_and_docs_are_present_and_do_not_contain_real_secrets():
    required = [
        PROJECT_ROOT / "Dockerfile",
        PROJECT_ROOT / "docker-compose.yml",
        PROJECT_ROOT / "docker-compose.prod.example.yml",
        PROJECT_ROOT / "nginx" / "nginx.conf.example",
        PROJECT_ROOT / "docs" / "DEPLOYMENT.md",
        PROJECT_ROOT / "docs" / "OPERATIONS_RUNBOOK.md",
        PROJECT_ROOT / "docs" / "SECURITY_CHECKLIST.md",
        PROJECT_ROOT / ".github" / "workflows" / "ci.yml",
    ]
    for path in required:
        assert path.exists(), f"{path} should exist"
        text = path.read_text(encoding="utf-8")
        for forbidden in ["sk-", "ghp_", "xoxb-", "-----BEGIN", "live_secret"]:
            assert forbidden not in text


def test_security_checklist_contains_required_boundaries():
    text = (PROJECT_ROOT / "docs" / "SECURITY_CHECKLIST.md").read_text(encoding="utf-8").lower()

    assert "production auth" in text
    assert "no local admin fallback" in text
    assert "no broker" in text
    assert "no auto trading" in text
    assert "no ai api" in text
    assert "hashed" in text


def test_no_real_env_committed():
    assert not (PROJECT_ROOT / ".env").exists()


def test_v26_source_keeps_safety_boundaries():
    import scripts.startup_check as startup_check
    import src.api.v2.server as server

    combined = "\n".join(
        [
            inspect.getsource(startup_check),
            inspect.getsource(server),
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto" + "order",
        "place_" + "order",
        "open" + "ai",
        "stripe." + "checkout",
        "payment_" + "secret",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in combined

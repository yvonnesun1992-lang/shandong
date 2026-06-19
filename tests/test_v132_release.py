from __future__ import annotations

import inspect
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.v2.server import create_v2_api_app, v132_response
from src.config import platform_config
from src.core.account import AccountContext, create_account_context
from src.core.cache_manager import StrategyCacheManager
from src.dashboard.system_admin import build_system_admin_panel
from src.plugins import create_default_registry


def test_docker_deploy_files_are_present_and_safe():
    dockerfile = Path("deploy/Dockerfile")
    compose = Path("deploy/docker-compose.yml")
    env_example = Path("deploy/.env.example")

    assert dockerfile.exists()
    assert compose.exists()
    assert env_example.exists()

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [dockerfile, compose, env_example])
    assert "streamlit run app/main.py" in combined
    assert "uvicorn src.api.v2.server:app" in combined
    assert "API" + "_KEY" not in combined
    assert "SEC" + "RET" not in combined
    assert "TOK" + "EN" not in combined


def test_v2_api_uses_stable_release_response_shape():
    payload = v132_response({"ok": True}, started_at=0.0, warning=["demo"])

    assert payload["success"] is True
    assert payload["data"] == {"ok": True}
    assert payload["meta"]["version"] == "V1.32"
    assert "latency_ms" in payload["meta"]
    assert payload["warning"] == ["demo"]


def test_v2_api_endpoints_are_available():
    client = TestClient(create_v2_api_app())
    endpoints = [
        "/api/v2/health",
        "/api/v2/dashboard/summary",
        "/api/v2/admin/system",
        "/api/v2/report/list",
        "/api/v2/trend",
        "/api/v2/compare",
        "/api/v2/risk",
    ]

    for path in endpoints:
        response = client.get(path, params={"user_id": "alice"})
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["meta"]["version"] == "V1.32"
        assert isinstance(body["warning"], list)


def test_v2_report_generation_and_detail_are_isolated():
    client = TestClient(create_v2_api_app())

    generated = client.post("/api/v2/report/generate", json={"user_id": "alice", "strategy_name": "trend_default"})
    detail = client.get("/api/v2/report/detail", params={"user_id": "alice", "report_id": "demo"})

    assert generated.status_code == 200
    assert detail.status_code == 200
    assert generated.json()["data"]["user"]["user_id"] == "alice"
    assert "data/users/alice/reports/demo" in detail.json()["data"]["report_path"]


def test_account_context_creates_user_isolated_paths():
    alice = create_account_context("alice@example.com")
    bob = create_account_context("bob@example.com")

    assert isinstance(alice, AccountContext)
    assert alice.user_id == "alice_example.com"
    assert alice.user_root == Path("data/users/alice_example.com")
    assert alice.report_dir != bob.report_dir
    assert alice.cache_dir != bob.cache_dir
    assert alice.dashboard_dir != bob.dashboard_dir
    assert alice.report_path("demo").as_posix().endswith("data/users/alice_example.com/reports/demo")


def test_system_admin_panel_reports_platform_metrics():
    cache = StrategyCacheManager()
    cache.set_dashboard("summary", {"ok": True})
    assert cache.get_dashboard("summary") == {"ok": True}
    registry = create_default_registry()

    panel = build_system_admin_panel(cache=cache, registry=registry, error_logs=["sample"])

    assert "api_latency_ms" in panel
    assert panel["cache"]["hit_rate"] >= 0
    assert panel["system_health_score"] >= 0
    assert set(panel["plugins"]["loaded"]) == {"dashboard", "report", "risk", "strategy"}
    assert panel["error_logs"] == ["sample"]


def test_platform_config_defaults_are_release_safe():
    assert platform_config.CACHE_ENABLED is True
    assert platform_config.API_ENABLED is True
    assert platform_config.MULTI_USER is True
    assert platform_config.LOG_LEVEL in {"DEBUG", "INFO", "WARNING", "ERROR"}


def test_v132_source_keeps_release_safety_boundaries():
    import src.api.v2.server as api_v2
    import src.config.platform_config as config
    import src.core.account as account
    import src.dashboard.system_admin as admin

    combined = "\n".join(
        [
            inspect.getsource(api_v2),
            inspect.getsource(config),
            inspect.getsource(account),
            inspect.getsource(admin),
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto " + "trading",
        "place_" + "order",
        "real " + "trading",
        "open" + "ai",
        "api_" + "key",
        "sec" + "ret=",
        "pass" + "word=",
        "tok" + "en=",
        "ev" + "al(",
        "ex" + "ec(",
    ]
    for word in forbidden:
        assert word not in combined

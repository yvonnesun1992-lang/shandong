from __future__ import annotations

import inspect

from fastapi.testclient import TestClient

from app.platform import initialize_platform
from src.api.server import create_api_app
from src.core.user_context import UserContext
from src.plugins import (
    DashboardPlugin,
    PluginRegistry,
    ReportPlugin,
    RiskPlugin,
    StrategyPlugin,
)


def test_plugin_system_registers_and_runs_plugins():
    registry = PluginRegistry()
    registry.register(ReportPlugin())
    registry.register(StrategyPlugin())
    registry.register(RiskPlugin())
    registry.register(DashboardPlugin())

    assert sorted(registry.names()) == ["dashboard", "report", "risk", "strategy"]
    result = registry.run("report", {"user_id": "alice"})

    assert result["status"] == "success"
    assert result["plugin"] == "report"


def test_api_standard_response_works():
    client = TestClient(create_api_app())

    response = client.get("/api/dashboard/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert isinstance(payload["data"], dict)
    assert isinstance(payload["warning"], list)


def test_api_report_endpoints_work():
    client = TestClient(create_api_app())

    generated = client.post("/api/report/generate", json={"user_id": "alice", "strategy_name": "trend_default"})
    listed = client.get("/api/report/list", params={"user_id": "alice"})
    detail = client.get("/api/report/detail", params={"user_id": "alice", "report_id": "demo"})

    assert generated.status_code == 200
    assert listed.status_code == 200
    assert detail.status_code == 200
    assert generated.json()["status"] == "success"
    assert listed.json()["status"] == "success"
    assert detail.json()["status"] == "success"


def test_api_analysis_endpoints_work():
    client = TestClient(create_api_app())
    for path in ["/api/trend", "/api/compare", "/api/risk"]:
        response = client.get(path, params={"user_id": "alice"})
        assert response.status_code == 200
        assert response.json()["status"] == "success"


def test_user_isolation_paths_and_keys_are_separate():
    alice = UserContext("alice")
    bob = UserContext("bob")

    assert alice.report_namespace != bob.report_namespace
    assert alice.cache_key("dashboard") != bob.cache_key("dashboard")
    assert alice.dashboard_key("summary") != bob.dashboard_key("summary")
    assert "alice" in alice.report_namespace


def test_platform_launcher_initializes_components():
    platform = initialize_platform(user_id="alice")

    assert platform["status"] == "ready"
    assert platform["user_context"].user_id == "alice"
    assert "report" in platform["plugins"].names()
    assert platform["cache"].stats()["cache_size"] == 0
    assert platform["api_app"].title == "Shandong Strategy Platform API"


def test_v131_modules_keep_research_only_boundaries():
    import app.platform as platform
    import src.api.server as api_server
    import src.core.user_context as user_context
    import src.plugins as plugins

    combined = "\n".join(
        [
            inspect.getsource(platform),
            inspect.getsource(api_server),
            inspect.getsource(user_context),
            inspect.getsource(plugins),
        ]
    )
    forbidden = [
        "IB" + "KR",
        "富" + "途",
        "Al" + "paca",
        "Robin" + "hood",
        "broker " + "order",
        "place_" + "order",
        "auto " + "trade",
        "api_" + "key=",
        "sec" + "ret=",
        "tok" + "en=",
        "Open" + "AI API",
        "AI " + "prediction",
        "ev" + "al(",
        "ex" + "ec(",
    ]
    for word in forbidden:
        assert word not in combined

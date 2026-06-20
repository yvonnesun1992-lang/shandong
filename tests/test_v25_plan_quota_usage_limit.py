from __future__ import annotations

import inspect
import json
from pathlib import Path

from fastapi.testclient import TestClient


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def configure_env(monkeypatch, tmp_path, auth_mode: str = "local") -> str:
    from src.config import database_config

    monkeypatch.setenv("SHANDONG_AUTH_MODE", auth_mode)
    db_url = sqlite_url(tmp_path / f"{auth_mode}.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)
    return db_url


def test_plan_limits_are_available_and_env_override_falls_back(monkeypatch):
    from src.config.plan_config import get_plan_limits

    monkeypatch.setenv("SHANDONG_FREE_MAX_REPORTS_PER_DAY", "bad")

    assert get_plan_limits("free")["max_reports_per_day"] == 10
    assert get_plan_limits("pro")["max_api_calls_per_day"] == 5000
    assert get_plan_limits("team")["max_workspace_members"] == 20


def test_workspace_plan_can_be_read_and_set(tmp_path, monkeypatch):
    from src.billing.plan_service import get_workspace_plan, set_workspace_plan

    configure_env(monkeypatch, tmp_path)

    assert get_workspace_plan("alpha")["plan_name"] == "free"
    assert set_workspace_plan("alpha", "pro")["plan_name"] == "pro"
    assert get_workspace_plan("alpha")["limits"]["max_api_keys"] == 5


def test_usage_events_record_daily_counts_and_sanitize_metadata(tmp_path, monkeypatch):
    from src.billing.usage_service import get_daily_usage, record_usage
    from src.config import database_config
    from src.db.usage_repository import UsageRepository

    configure_env(monkeypatch, tmp_path)
    record_usage("alpha", "alice", "api_call", metadata={"authorization": "Bearer raw", "password": "hidden", "ok": True})
    record_usage("alpha", "alice", "api_call", quantity=2)

    events = UsageRepository(database_config.DATABASE_URL).list_usage_events("alpha", event_type="api_call")
    text = json.dumps(events, ensure_ascii=False).lower()

    assert get_daily_usage("alpha", "api_call") == 3
    assert "hidden" not in text
    assert "bearer raw" not in text
    assert events[0]["metadata_json"]["ok"] is True


def test_quota_exceeded_for_report_generation(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.billing.usage_service import record_usage

    configure_env(monkeypatch, tmp_path)
    for _ in range(10):
        record_usage("default", "default", "report_generate")

    client = TestClient(create_v2_api_app())
    response = client.post("/api/v2/report/generate", json={"strategy_name": "trend_default"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "QUOTA_EXCEEDED"


def test_quota_exceeded_for_api_call(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.billing.usage_service import record_usage

    configure_env(monkeypatch, tmp_path)
    for _ in range(500):
        record_usage("default", "default", "api_call")

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/reports/db-list")

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "QUOTA_EXCEEDED"


def test_billing_plan_quota_and_health_endpoints(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app

    configure_env(monkeypatch, tmp_path)
    client = TestClient(create_v2_api_app())

    plan = client.get("/api/v2/billing/plan")
    quota = client.get("/api/v2/billing/quota")
    health = client.get("/api/v2/system/billing-health")

    assert plan.status_code == 200
    assert plan.json()["data"]["plan"]["plan_name"] == "free"
    assert quota.status_code == 200
    assert quota.json()["data"]["quota"]["workspace_id"] == "default"
    assert health.status_code == 200
    assert health.json()["data"]["billing"]["real_payment_enabled"] is False
    assert health.json()["data"]["billing"]["usage_tracking_ready"] is True


def test_v25_source_keeps_safety_boundaries():
    import src.api.v2.server as server
    import src.billing.plan_service as plan_service
    import src.billing.quota_service as quota_service
    import src.billing.usage_service as usage_service
    import src.config.plan_config as plan_config
    import src.db.usage_repository as usage_repository

    combined = "\n".join(
        [
            inspect.getsource(server),
            inspect.getsource(plan_config),
            inspect.getsource(usage_repository),
            inspect.getsource(plan_service),
            inspect.getsource(quota_service),
            inspect.getsource(usage_service),
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto" + "order",
        "place_" + "order",
        "open" + "ai",
        "stripe." + "checkout",
        "payment_" + "secret",
        "password=",
        "token=",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in combined

from __future__ import annotations

import importlib
import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_observability_config_files_and_defaults(monkeypatch):
    assert (ROOT / "src/config/observability_config.py").exists()
    assert (ROOT / "src/observability/metrics.py").exists()

    monkeypatch.delenv("SHANDONG_OBSERVABILITY_MODE", raising=False)
    monkeypatch.delenv("SHANDONG_OBSERVABILITY_PROVIDER", raising=False)
    config = importlib.import_module("src.config.observability_config")
    config = importlib.reload(config)

    assert config.observability_mode() == "local"
    assert config.observability_provider() == "local"
    assert config.local_observability_enabled() is True
    assert config.external_observability_enabled() is False


def test_local_metrics_collector_records_aggregate_data():
    metrics = importlib.import_module("src.observability.metrics")
    metrics.reset_api_metrics()

    metrics.record_api_metric("/api/v2/health", "ok", 12.5, warning_count=1)
    metrics.record_api_metric("/api/v2/health", "ok", 20.0)
    api_summary = metrics.get_api_metrics_summary()

    assert api_summary["total_requests"] == 2
    assert api_summary["by_path"]["/api/v2/health"]["count"] == 2
    assert api_summary["by_path"]["/api/v2/health"]["warning_count"] == 1
    assert api_summary["average_latency_ms"] > 0

    metrics.record_health_snapshot("readiness", "ok", warning_count=0, error_count=0)
    timeline = metrics.get_health_timeline_summary()

    assert timeline["total_snapshots"] >= 1
    assert timeline["latest"]["name"] == "readiness"
    assert timeline["latest"]["status"] == "ok"


def test_observability_endpoint_returns_sanitized_summary(monkeypatch):
    monkeypatch.delenv("SHANDONG_OBSERVABILITY_MODE", raising=False)
    monkeypatch.delenv("SHANDONG_OBSERVABILITY_PROVIDER", raising=False)

    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/observability")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    observability = payload["data"]["observability"]
    assert observability["mode"] == "local"
    assert observability["provider"] == "local"
    assert observability["external_provider_enabled"] is False
    assert "api_metrics" in observability
    assert "health_timeline" in observability

    lowered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in [
        "secret",
        "token",
        "password",
        "api_key",
        "session_id",
        "authorization",
        "/users/apple",
    ]:
        assert forbidden not in lowered


def test_frontend_and_admin_observability_surface():
    api_client = read_text("web/frontend/app/lib/apiClient.ts")
    admin_page = read_text("web/frontend/app/admin/page.tsx")

    assert "fetchObservability" in api_client
    assert "/api/v2/system/observability" in api_client
    assert "Observability" in admin_page
    assert "Local observability" in admin_page
    assert "External provider: not connected" in admin_page
    assert "API metrics: available" in admin_page
    assert "Health timeline: available" in admin_page
    assert "Log export: not connected" in admin_page


def test_observability_docs_readme_and_review_package_exist():
    docs = read_text("docs/OBSERVABILITY_PLAN.md")
    readme = read_text("README.md")
    review = read_text("REVIEW_PACKAGE.md")

    assert "Current State" in docs
    assert "What Is Collected" in docs
    assert "What Is Not Collected" in docs
    assert "No Sentry" in docs
    assert "No Datadog" in docs
    assert "No external log upload" in docs
    assert "V3.4" in readme
    assert "Observability / Logs / Metrics Planning" in readme
    assert "V3.4" in review
    assert "可观测性规划" in review or "observability planning" in review.lower()


def test_v34_runtime_boundaries():
    runtime_files = [
        "src/config/observability_config.py",
        "src/observability/metrics.py",
        "src/api/v2/server.py",
        "web/frontend/app/admin/page.tsx",
    ]
    combined = "\n".join(read_text(path) for path in runtime_files).lower()

    forbidden = [
        "sentry_sdk",
        "datadog",
        "newrelic",
        "grafana cloud",
        "remote_write",
        "external log upload",
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

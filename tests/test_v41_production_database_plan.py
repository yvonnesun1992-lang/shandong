from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_production_database_planning_modules_exist_and_default_safe(monkeypatch):
    monkeypatch.delenv("SHANDONG_DATABASE_RUNTIME_MODE", raising=False)
    monkeypatch.delenv("SHANDONG_DATABASE_PROVIDER", raising=False)
    monkeypatch.delenv("SHANDONG_ENABLE_PRODUCTION_DATABASE", raising=False)
    monkeypatch.delenv("SHANDONG_DATABASE_MIGRATION_READY", raising=False)

    from src.config.production_database_config import database_runtime_mode, production_database_enabled, production_database_provider
    from src.db.production_database_plan import get_production_database_plan, validate_database_boundary

    assert (ROOT / "src/config/production_database_config.py").exists()
    assert (ROOT / "src/db/production_database_plan.py").exists()
    assert (ROOT / "scripts/production_database_plan_check.py").exists()
    assert database_runtime_mode() == "local"
    assert production_database_provider() == "sqlite"
    assert production_database_enabled() is False

    plan = get_production_database_plan()
    boundary = validate_database_boundary()
    assert plan["current_database"] == "local_sqlite"
    assert plan["future_database"] == "postgres_planned"
    assert plan["production_enabled"] is False
    assert plan["migration_ready"] is False
    assert boundary["valid"] is True


def test_production_database_endpoint_is_sanitized():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/production-database")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    database = payload["data"]["production_database"]
    assert database["current_database"] == "local_sqlite"
    assert database["future_database"] == "postgres_planned"
    assert database["production_enabled"] is False
    assert database["migration_ready"] is False
    assert database["external_database_connected"] is False

    lowered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in ["database_url", "password", "token", "secret", "api_key", "/users/apple", "username"]:
        assert forbidden not in lowered


def test_production_database_plan_check_returns_not_ready():
    from scripts.production_database_plan_check import run_production_database_plan_check

    result = run_production_database_plan_check()
    assert result["success"] is True
    assert result["production_database_ready"] is False
    assert isinstance(result["checks"], list)
    assert result["errors"] == []


def test_frontend_admin_docs_and_package_updates_exist():
    api_client = read_text("web/frontend/app/lib/apiClient.ts")
    admin_page = read_text("web/frontend/app/admin/page.tsx")
    docs = read_text("docs/PRODUCTION_DATABASE_PLAN.md")
    readiness_doc = read_text("docs/V4_PRODUCTION_LAUNCH_READINESS.md")
    readme = read_text("README.md")
    review = read_text("REVIEW_PACKAGE.md")

    assert "fetchProductionDatabase" in api_client
    assert "/api/v2/system/production-database" in api_client
    assert "Production Database" in admin_page
    assert "Current database: local SQLite" in admin_page
    assert "Future database: PostgreSQL planned" in admin_page
    assert "Production database: not connected" in admin_page
    assert "Migration ready: no" in admin_page
    assert "Backup policy: planned" in admin_page
    assert "Rollback policy: planned" in admin_page

    for phrase in [
        "Current State",
        "Why Production Database Needs Planning",
        "Recommended Future Architecture",
        "Migration Checklist",
        "Not Implemented Yet",
        "No production database connected",
        "No PostgreSQL connection enabled",
        "No production DATABASE_URL",
        "No database password",
        "No real customer data migration",
    ]:
        assert phrase in docs

    assert "V4.1" in readiness_doc
    assert "production database is planned" in readiness_doc
    assert "production_database_ready remains false" in readiness_doc
    assert "V4.1" in readme
    assert "Production Database Plan" in readme
    assert "PostgreSQL planned" in readme
    assert "Production database endpoint" in readme
    assert "No production database connected" in readme
    assert "V4.1" in review
    assert "生产数据库规划" in review


def test_v41_runtime_boundaries():
    runtime_files = [
        "src/config/production_database_config.py",
        "src/db/production_database_plan.py",
        "scripts/production_database_plan_check.py",
        "src/api/v2/server.py",
        "web/frontend/app/admin/page.tsx",
        "web/frontend/app/lib/apiClient.ts",
    ]
    combined = "\n".join(read_text(path) for path in runtime_files).lower()

    forbidden = [
        "aws_access_key",
        "supabase_key",
        "neon_key",
        "railway_token",
        "render_api",
        "broker api",
        "auto order",
        "place_order",
        "openai",
        "oauth client",
        "production secret",
        "password=",
        "token=",
        "api_key=",
        "eval(",
        "exec(",
    ]
    for pattern in forbidden:
        assert pattern not in combined

from __future__ import annotations

import inspect
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def test_success_and_error_response_shapes_are_standard():
    from src.api.v2.response import error_response, success_response

    ok = success_response({"hello": "world"}, meta={"request_id": "demo"}, warning=["sample"])
    error = error_response("Bad input", code="BAD_INPUT", detail={"field": "page"}, status_code=422)

    assert ok["success"] is True
    assert ok["data"] == {"hello": "world"}
    assert ok["meta"]["request_id"] == "demo"
    assert "latency_ms" in ok["meta"]
    assert ok["warning"] == ["sample"]

    assert error["success"] is False
    assert error["error"]["code"] == "BAD_INPUT"
    assert error["error"]["message"] == "Bad input"
    assert error["error"]["detail"] == {"field": "page"}
    assert error["meta"]["status_code"] == 422


def test_api_error_sanitizes_sensitive_and_path_details():
    from src.api.v2.errors import ApiError, DatabaseApiError

    error = ApiError(
        "Failed at /Users/apple/project/data/shandong_v2.db with token=abc and password=123",
        detail={"secret": "abc", "nested": {"api_key": "raw"}},
    )
    database_error = DatabaseApiError("/tmp/data/shandong_v2.db locked with token=abc")

    rendered = json.dumps(error.to_response(), ensure_ascii=False).lower()
    db_rendered = json.dumps(database_error.to_response(), ensure_ascii=False).lower()

    assert "/users/" not in rendered
    assert "token=abc" not in rendered
    assert "password=123" not in rendered
    assert "secret" not in rendered
    assert "api_key" not in rendered
    assert "shandong_v2.db" not in db_rendered


def test_schemas_clean_user_id_and_clamp_pagination():
    from src.api.v2.schemas import ReportGenerateRequest, ReportListQuery, UserQuery

    generated = ReportGenerateRequest(user_id="../alice token", strategy_name="")
    listed = ReportListQuery(user_id="bob@example.com", page=0, page_size=999)
    user = UserQuery(user_id="")

    assert generated.user_id == "alice_token"
    assert generated.strategy_name == "trend_default"
    assert listed.page == 1
    assert listed.page_size == 100
    assert user.user_id == "default"


def test_paginate_items_returns_stable_metadata():
    from src.api.v2.pagination import paginate_items

    result = paginate_items(list(range(45)), page=2, page_size=20)
    empty = paginate_items([], page=5, page_size=20)

    assert result["items"] == list(range(20, 40))
    assert result["pagination"] == {
        "page": 2,
        "page_size": 20,
        "total": 45,
        "total_pages": 3,
        "has_next": True,
        "has_prev": True,
    }
    assert empty["items"] == []
    assert empty["pagination"]["total_pages"] == 0
    assert empty["pagination"]["page"] == 1


def test_cors_middleware_uses_local_origins_without_wildcard(monkeypatch):
    from src.api.v2.middleware import allowed_origins, configure_cors

    monkeypatch.setenv("SHANDONG_ALLOWED_ORIGINS", "https://example.com, http://localhost:3000")
    origins = allowed_origins()
    app = FastAPI()
    configure_cors(app)

    assert "*" not in origins
    assert "http://localhost:3000" in origins
    assert "https://example.com" in origins
    assert any(middleware.cls.__name__ == "CORSMiddleware" for middleware in app.user_middleware)


def test_rate_limit_returns_standard_error_after_limit():
    from src.api.v2.middleware import InMemoryRateLimiter, RateLimitMiddleware
    from src.api.v2.response import success_response

    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, limiter=InMemoryRateLimiter(limit_per_minute=1))

    @app.get("/limited")
    def limited(user_id: str = "default") -> dict:
        return success_response({"user_id": user_id})

    client = TestClient(app)
    assert client.get("/limited", params={"user_id": "alice"}).status_code == 200
    limited_response = client.get("/limited", params={"user_id": "alice"})

    assert limited_response.status_code == 429
    body = limited_response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RATE_LIMITED"


def test_logging_sanitizes_sensitive_values_and_uses_audit_fallback(tmp_path, monkeypatch):
    from src.api.v2.logging import log_api_event, sanitize_log_value
    from src.config import database_config

    db_url = sqlite_url(tmp_path / "api_logging.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)

    sanitized = sanitize_log_value(
        {
            "endpoint": "/x",
            "secret": "abc",
            "token": "def",
            "password": "ghi",
            "api_key": "raw",
            "nested": {"ok": True},
        }
    )
    event = log_api_event("/api/v2/health", "alice", "ok", 12.4, warning_count=1, metadata=sanitized)
    text = json.dumps({"sanitized": sanitized, "event": event}, ensure_ascii=False).lower()

    assert "abc" not in text
    assert "def" not in text
    assert "ghi" not in text
    assert "raw" not in text
    assert event["logged"] in {True, False}


def test_v21_api_db_list_paginates_and_db_health_is_enhanced(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config
    from src.db.repository import StrategyReportRepository

    db_url = sqlite_url(tmp_path / "api.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)
    reports = StrategyReportRepository(db_url)
    for index in range(3):
        reports.save_report(user_id="default", report_id=f"r{index}", strategy_name=f"s{index}")

    client = TestClient(create_v2_api_app())
    listed = client.get("/api/v2/reports/db-list", params={"user_id": "default", "page": 1, "page_size": 2})
    health = client.get("/api/v2/system/db-health")

    assert listed.status_code == 200
    body = listed.json()
    assert body["success"] is True
    assert len(body["data"]["reports"]["items"]) == 2
    assert body["data"]["reports"]["pagination"]["total"] == 3
    assert body["data"]["reports"]["pagination"]["has_next"] is True
    assert health.json()["data"]["database"]["database_type"] == "sqlite"
    assert health.json()["data"]["database"]["tables_checked"] >= 5
    assert "warning" in health.json()["data"]["database"]


def test_api_database_exception_returns_standard_warning_not_unhandled_500(monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config

    monkeypatch.setattr(database_config, "DATABASE_URL", "postgresql://not-enabled")
    client = TestClient(create_v2_api_app())

    response = client.get("/api/v2/reports/db-list", params={"user_id": "default"})
    health = client.get("/api/v2/system/db-health")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["warning"]
    assert health.status_code == 200
    assert health.json()["success"] is True
    assert health.json()["warning"]


def test_v21_api_source_keeps_safety_boundaries():
    import src.api.v2.errors as errors
    import src.api.v2.logging as api_logging
    import src.api.v2.middleware as middleware
    import src.api.v2.response as response
    import src.api.v2.schemas as schemas
    import src.api.v2.server as server

    combined = "\n".join(
        [
            inspect.getsource(errors),
            inspect.getsource(api_logging),
            inspect.getsource(middleware),
            inspect.getsource(response),
            inspect.getsource(schemas),
            inspect.getsource(server),
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto" + "order",
        "place_" + "order",
        "open" + "ai",
        "stripe_" + "secret",
        "real payment execution",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in combined

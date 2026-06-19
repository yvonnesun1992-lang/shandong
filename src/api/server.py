from __future__ import annotations

from fastapi import FastAPI

from src.core.user_context import UserContext
from src.plugins import create_default_registry
from src.reports.strategy_research_dashboard import build_strategy_research_dashboard
from src.reports.strategy_report_compare import compare_strategy_research_reports
from src.reports.strategy_report_trend import build_strategy_report_trend


def api_response(data: dict | list | None = None, warning: list[str] | None = None, status: str = "success") -> dict:
    return {"status": status, "data": data if data is not None else {}, "warning": warning or []}


def create_api_app() -> FastAPI:
    app = FastAPI(title="Shandong Strategy Platform API")
    registry = create_default_registry()

    @app.post("/api/report/generate")
    def generate_report(payload: dict | None = None) -> dict:
        payload = payload or {}
        user = UserContext(payload.get("user_id"))
        plugin_result = registry.run("report", {"user_id": user.user_id, "strategy_name": payload.get("strategy_name", "trend_default")})
        return api_response({"user": user.as_dict(), "plugin": plugin_result})

    @app.get("/api/report/list")
    def list_reports(user_id: str = "default") -> dict:
        user = UserContext(user_id)
        return api_response({"user": user.as_dict(), "reports": []})

    @app.get("/api/report/detail")
    def report_detail(report_id: str, user_id: str = "default") -> dict:
        user = UserContext(user_id)
        return api_response({"user": user.as_dict(), "report_key": user.report_key(report_id), "report": {}})

    @app.get("/api/trend")
    def trend(user_id: str = "default") -> dict:
        user = UserContext(user_id)
        trend_report = build_strategy_report_trend([], None)
        return api_response({"user": user.as_dict(), "trend": trend_report})

    @app.get("/api/compare")
    def compare(user_id: str = "default") -> dict:
        user = UserContext(user_id)
        comparison = compare_strategy_research_reports([])
        return api_response({"user": user.as_dict(), "comparison": comparison})

    @app.get("/api/risk")
    def risk(user_id: str = "default") -> dict:
        user = UserContext(user_id)
        plugin_result = registry.run("risk", {"user_id": user.user_id})
        return api_response({"user": user.as_dict(), "risk": plugin_result})

    @app.get("/api/dashboard/summary")
    def dashboard_summary(user_id: str = "default") -> dict:
        user = UserContext(user_id)
        dashboard = build_strategy_research_dashboard([])
        return api_response({"user": user.as_dict(), "dashboard": dashboard})

    return app


app = create_api_app()

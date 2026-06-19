from __future__ import annotations

from time import perf_counter

from fastapi import FastAPI

from src.config.platform_config import PLATFORM_VERSION
from src.core.account import create_account_context
from src.core.cache_manager import StrategyCacheManager
from src.dashboard.system_admin import build_system_admin_panel
from src.plugins import create_default_registry
from src.reports.strategy_research_dashboard import build_strategy_research_dashboard
from src.reports.strategy_report_compare import compare_strategy_research_reports
from src.reports.strategy_report_trend import build_strategy_report_trend


def v132_response(data: dict | list | None = None, started_at: float | None = None, warning: list[str] | None = None) -> dict:
    start = perf_counter() if started_at is None else float(started_at)
    latency_ms = max((perf_counter() - start) * 1000, 0.0)
    return {
        "success": True,
        "data": data if data is not None else {},
        "meta": {
            "version": PLATFORM_VERSION,
            "latency_ms": round(latency_ms, 2),
        },
        "warning": warning or [],
    }


def create_v2_api_app() -> FastAPI:
    api = FastAPI(title="Shandong Strategy Platform API V2")
    registry = create_default_registry()
    cache = StrategyCacheManager(default_ttl_seconds=900)

    @api.get("/api/v2/health")
    def health(user_id: str = "default") -> dict:
        started = perf_counter()
        account = create_account_context(user_id)
        return v132_response({"status": "ok", "user": account.as_dict()}, started_at=started)

    @api.post("/api/v2/report/generate")
    def generate_report(payload: dict | None = None) -> dict:
        started = perf_counter()
        payload = payload or {}
        account = create_account_context(payload.get("user_id"))
        strategy_name = payload.get("strategy_name", "trend_default")
        plugin_result = registry.run("report", {"user_id": account.user_id, "strategy_name": strategy_name})
        return v132_response({"user": account.as_dict(), "plugin": plugin_result}, started_at=started)

    @api.get("/api/v2/report/list")
    def list_reports(user_id: str = "default") -> dict:
        started = perf_counter()
        account = create_account_context(user_id)
        return v132_response({"user": account.as_dict(), "reports": []}, started_at=started)

    @api.get("/api/v2/report/detail")
    def report_detail(report_id: str, user_id: str = "default") -> dict:
        started = perf_counter()
        account = create_account_context(user_id)
        return v132_response(
            {
                "user": account.as_dict(),
                "report_path": account.report_path(report_id).as_posix(),
                "report": {},
            },
            started_at=started,
        )

    @api.get("/api/v2/trend")
    def trend(user_id: str = "default") -> dict:
        started = perf_counter()
        account = create_account_context(user_id)
        trend_report = build_strategy_report_trend([], None)
        cache.set_trend(account.cache_path("trend").as_posix(), trend_report)
        return v132_response({"user": account.as_dict(), "trend": trend_report}, started_at=started)

    @api.get("/api/v2/compare")
    def compare(user_id: str = "default") -> dict:
        started = perf_counter()
        account = create_account_context(user_id)
        comparison = compare_strategy_research_reports([])
        cache.set_compare(account.cache_path("compare").as_posix(), comparison)
        return v132_response({"user": account.as_dict(), "comparison": comparison}, started_at=started)

    @api.get("/api/v2/risk")
    def risk(user_id: str = "default") -> dict:
        started = perf_counter()
        account = create_account_context(user_id)
        plugin_result = registry.run("risk", {"user_id": account.user_id})
        return v132_response({"user": account.as_dict(), "risk": plugin_result}, started_at=started)

    @api.get("/api/v2/dashboard/summary")
    def dashboard_summary(user_id: str = "default") -> dict:
        started = perf_counter()
        account = create_account_context(user_id)
        dashboard = build_strategy_research_dashboard([])
        cache.set_dashboard(account.dashboard_path("summary").as_posix(), dashboard)
        return v132_response({"user": account.as_dict(), "dashboard": dashboard}, started_at=started)

    @api.get("/api/v2/admin/system")
    def system_admin(user_id: str = "default") -> dict:
        started = perf_counter()
        account = create_account_context(user_id)
        admin_panel = build_system_admin_panel(cache=cache, registry=registry)
        return v132_response({"user": account.as_dict(), "admin": admin_panel}, started_at=started)

    return api


app = create_v2_api_app()

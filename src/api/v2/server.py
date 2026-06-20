from __future__ import annotations

from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.api.v2.auth import audit_auth_event, build_auth_context, require_permission
from src.api.v2.errors import ApiError, DatabaseApiError, ValidationApiError
from src.api.v2.logging import log_api_event
from src.api.v2.middleware import InMemoryRateLimiter, RateLimitMiddleware, configure_cors
from src.api.v2.pagination import paginate_items
from src.api.v2.response import success_response
from src.api.v2.schemas import ReportGenerateRequest, ReportListQuery, UserQuery
from src.auth.permission_service import set_user_role
from src.auth.session_service import create_session, get_session, revoke_session

from src.config import database_config
from src.core.account import create_account_context
from src.core.cache_manager import StrategyCacheManager
from src.dashboard.system_admin import build_system_admin_panel
from src.db.migrations import initialize_database
from src.db.repository import StrategyReportRepository, UserRepository
from src.plugins import create_default_registry
from src.reports.strategy_research_dashboard import build_strategy_research_dashboard
from src.reports.strategy_report_compare import compare_strategy_research_reports
from src.reports.strategy_report_trend import build_strategy_report_trend
from src.security.policy import get_security_policy


def v132_response(data: dict | list | None = None, started_at: float | None = None, warning: list[str] | None = None) -> dict:
    return success_response(data=data, started_at=started_at, warning=warning)


def database_type(database_url: str) -> str:
    if database_url.startswith("sqlite:///"):
        return "sqlite"
    if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
        return "postgresql"
    return "unknown"


def warning_from_exception(prefix: str, exc: Exception) -> list[str]:
    return [f"{prefix}: {type(exc).__name__}"]


def create_v2_api_app() -> FastAPI:
    api = FastAPI(title="Shandong Strategy Platform API V2")
    configure_cors(api)
    api.add_middleware(RateLimitMiddleware, limiter=InMemoryRateLimiter(limit_per_minute=120))
    registry = create_default_registry()
    cache = StrategyCacheManager(default_ttl_seconds=900)

    @api.exception_handler(ApiError)
    async def api_error_handler(_request: Request, exc: ApiError):
        return JSONResponse(status_code=exc.status_code, content=exc.to_response())

    @api.exception_handler(ValidationError)
    async def validation_error_handler(_request: Request, exc: ValidationError):
        error = ValidationApiError("Invalid request parameters", detail={"errors": exc.errors()})
        return JSONResponse(status_code=error.status_code, content=error.to_response())

    @api.get("/api/v2/health")
    def health(user_id: str = "default") -> dict:
        started = perf_counter()
        query = UserQuery(user_id=user_id)
        account = create_account_context(query.user_id)
        response = success_response({"status": "ok", "user": account.as_dict()}, started_at=started)
        log_api_event("/api/v2/health", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.post("/api/v2/report/generate")
    def generate_report(request: Request, payload: dict | None = None) -> dict:
        started = perf_counter()
        auth_context = require_permission(request, "report:write")
        report_request = ReportGenerateRequest(**(payload or {}))
        has_explicit_auth = bool(request.headers.get("X-Session-ID") or request.headers.get("X-API-Key"))
        account_user_id = auth_context.user_id if has_explicit_auth else report_request.user_id
        account = create_account_context(account_user_id)
        strategy_name = report_request.strategy_name
        plugin_result = registry.run("report", {"user_id": account.user_id, "strategy_name": strategy_name})
        response = success_response({"user": account.as_dict(), "plugin": plugin_result}, started_at=started)
        log_api_event("/api/v2/report/generate", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/report/list")
    def list_reports(user_id: str = "default", page: int = 1, page_size: int = 20) -> dict:
        started = perf_counter()
        query = ReportListQuery(user_id=user_id, page=page, page_size=page_size)
        account = create_account_context(query.user_id)
        reports = paginate_items([], page=query.page, page_size=query.page_size)
        response = success_response({"user": account.as_dict(), "reports": reports}, started_at=started)
        log_api_event("/api/v2/report/list", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/reports/db-list")
    def list_database_reports(request: Request, user_id: str = "default", page: int = 1, page_size: int = 20) -> dict:
        started = perf_counter()
        auth_context = require_permission(request, "report:read")
        query = ReportListQuery(user_id=auth_context.user_id or user_id, page=page, page_size=page_size)
        account = create_account_context(auth_context.user_id)
        try:
            report_items = StrategyReportRepository(database_config.DATABASE_URL).list_reports_by_user(account.user_id)
            reports = paginate_items(report_items, page=query.page, page_size=query.page_size)
            warning: list[str] = []
        except Exception as exc:
            reports = paginate_items([], page=query.page, page_size=query.page_size)
            warning = warning_from_exception("database unavailable", DatabaseApiError(str(exc)))
        response = success_response({"user": account.as_dict(), "reports": reports}, started_at=started, warning=warning)
        log_api_event("/api/v2/reports/db-list", account.user_id, "ok", response["meta"]["latency_ms"], len(warning))
        return response

    @api.get("/api/v2/users/default")
    def default_database_user() -> dict:
        started = perf_counter()
        try:
            users = UserRepository(database_config.DATABASE_URL)
            user = users.get_user_by_user_id("default") or users.create_user("default", role="admin", plan="free")
            warning: list[str] = []
        except Exception as exc:
            user = {"user_id": "default"}
            warning = warning_from_exception("database unavailable", DatabaseApiError(str(exc)))
        response = success_response({"user": user}, started_at=started, warning=warning)
        log_api_event("/api/v2/users/default", "default", "ok", response["meta"]["latency_ms"], len(warning))
        return response

    @api.get("/api/v2/system/db-health")
    def database_health() -> dict:
        started = perf_counter()
        db_type = database_type(database_config.DATABASE_URL)
        try:
            migration = initialize_database(database_config.DATABASE_URL)
            database = {
                "status": "ok",
                "storage_enabled": database_config.USE_DATABASE_STORAGE,
                "tables_checked": migration["tables"],
                "database_type": db_type,
                "warning": [],
            }
            warning: list[str] = []
        except Exception as exc:
            warning = warning_from_exception("database unavailable", DatabaseApiError(str(exc)))
            database = {
                "status": "warning",
                "storage_enabled": database_config.USE_DATABASE_STORAGE,
                "tables_checked": 0,
                "database_type": db_type,
                "warning": warning,
            }
        response = success_response({"database": database}, started_at=started, warning=warning)
        log_api_event("/api/v2/system/db-health", "default", "ok", response["meta"]["latency_ms"], len(warning))
        return response

    @api.get("/api/v2/system/security-health")
    def security_health() -> dict:
        started = perf_counter()
        policy = get_security_policy()
        security = policy.as_dict()
        audit_auth_event("default", "security.policy_checked", security)
        response = success_response({"security": security}, started_at=started, warning=security["warnings"])
        log_api_event("/api/v2/system/security-health", "default", "ok", response["meta"]["latency_ms"], len(security["warnings"]))
        return response

    @api.post("/api/v2/auth/login")
    def auth_login(payload: dict | None = None) -> dict:
        started = perf_counter()
        policy = get_security_policy()
        payload = payload or {}
        user_id = str(payload.get("user_id") or "default")
        role = str(payload.get("role") or "admin")
        user = set_user_role(user_id, role)
        session = create_session(user["user_id"], metadata={"role": user["role"]})
        session["role"] = user["role"]
        audit_auth_event(user["user_id"], "auth.login", {"role": user["role"]})
        warning = ["mock_auth_only"] if policy.auth_mode == "production" else []
        response = success_response(
            {"session": session},
            meta={"auth_mode": policy.auth_mode, "mock_auth_only": True},
            warning=warning,
            started_at=started,
        )
        log_api_event("/api/v2/auth/login", user["user_id"], "ok", response["meta"]["latency_ms"])
        return response

    @api.post("/api/v2/auth/logout")
    def auth_logout(payload: dict | None = None) -> dict:
        started = perf_counter()
        payload = payload or {}
        session_value = str(payload.get("session_id") or "")
        session_record = get_session(session_value) if session_value else None
        user_id = session_record.get("user_id", "default") if session_record else "default"
        revoked = revoke_session(session_value) if session_value else False
        audit_auth_event(user_id, "auth.logout", {"revoked": revoked})
        response = success_response({"revoked": revoked}, started_at=started)
        log_api_event("/api/v2/auth/logout", user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/auth/me")
    def auth_me(request: Request) -> dict:
        started = perf_counter()
        context = build_auth_context(request)
        audit_auth_event(context.user_id, "auth.me", {"authenticated": context.is_authenticated})
        response = success_response({"auth": context.as_dict()}, started_at=started)
        log_api_event("/api/v2/auth/me", context.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/report/detail")
    def report_detail(report_id: str, user_id: str = "default") -> dict:
        started = perf_counter()
        query = UserQuery(user_id=user_id)
        account = create_account_context(query.user_id)
        response = success_response(
            {
                "user": account.as_dict(),
                "report_path": account.report_path(report_id).as_posix(),
                "report": {},
            },
            started_at=started,
        )
        log_api_event("/api/v2/report/detail", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/trend")
    def trend(user_id: str = "default") -> dict:
        started = perf_counter()
        query = UserQuery(user_id=user_id)
        account = create_account_context(query.user_id)
        trend_report = build_strategy_report_trend([], None)
        cache.set_trend(account.cache_path("trend").as_posix(), trend_report)
        response = success_response({"user": account.as_dict(), "trend": trend_report}, started_at=started)
        log_api_event("/api/v2/trend", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/compare")
    def compare(user_id: str = "default") -> dict:
        started = perf_counter()
        query = UserQuery(user_id=user_id)
        account = create_account_context(query.user_id)
        comparison = compare_strategy_research_reports([])
        cache.set_compare(account.cache_path("compare").as_posix(), comparison)
        response = success_response({"user": account.as_dict(), "comparison": comparison}, started_at=started)
        log_api_event("/api/v2/compare", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/risk")
    def risk(request: Request, user_id: str = "default") -> dict:
        started = perf_counter()
        auth_context = require_permission(request, "risk:read")
        query = UserQuery(user_id=auth_context.user_id or user_id)
        account = create_account_context(query.user_id)
        plugin_result = registry.run("risk", {"user_id": account.user_id})
        response = success_response({"user": account.as_dict(), "risk": plugin_result}, started_at=started)
        log_api_event("/api/v2/risk", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/dashboard/summary")
    def dashboard_summary(request: Request, user_id: str = "default") -> dict:
        started = perf_counter()
        auth_context = require_permission(request, "dashboard:read")
        query = UserQuery(user_id=auth_context.user_id or user_id)
        account = create_account_context(query.user_id)
        dashboard = build_strategy_research_dashboard([])
        cache.set_dashboard(account.dashboard_path("summary").as_posix(), dashboard)
        response = success_response({"user": account.as_dict(), "dashboard": dashboard}, started_at=started)
        log_api_event("/api/v2/dashboard/summary", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/admin/system")
    def system_admin(request: Request, user_id: str = "default") -> dict:
        started = perf_counter()
        auth_context = require_permission(request, "admin:read")
        query = UserQuery(user_id=auth_context.user_id or user_id)
        account = create_account_context(query.user_id)
        admin_panel = build_system_admin_panel(cache=cache, registry=registry)
        response = success_response({"user": account.as_dict(), "admin": admin_panel}, started_at=started)
        log_api_event("/api/v2/admin/system", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    return api


app = create_v2_api_app()

from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.api.v2.admin_console import build_admin_console_summary
from src.api.v2.auth import audit_auth_event, build_auth_context, require_permission
from src.api.v2.errors import ApiError, DatabaseApiError, ValidationApiError
from src.api.v2.logging import log_api_event
from src.api.v2.middleware import InMemoryRateLimiter, RateLimitMiddleware, configure_cors
from src.api.v2.pagination import paginate_items
from src.api.v2.response import success_response
from src.api.v2.schemas import ReportGenerateRequest, ReportListQuery, UserQuery
from src.auth.permission_service import set_user_role
from src.auth.identity_provider import get_identity_provider_plan
from src.auth.session_service import create_session, get_session, revoke_session

from src.billing.plan_service import get_workspace_plan
from src.billing.quota_service import get_quota_status, require_quota
from src.billing.usage_service import record_usage
from src.config import database_config
from src.config.deployment_config import deployment_planning_status
from src.config.observability_config import observability_planning_status
from src.core.account import create_account_context
from src.core.cache_manager import StrategyCacheManager
from src.dashboard.system_admin import build_system_admin_panel
from src.db.migrations import initialize_database
from src.db.repository import StrategyReportRepository, UserRepository
from src.db.workspace_repository import WorkspaceRepository
from src.plugins import create_default_registry
from src.observability.metrics import get_api_metrics_summary, get_health_timeline_summary, record_health_snapshot
from src.reports.strategy_research_dashboard import build_strategy_research_dashboard
from src.reports.strategy_report_compare import compare_strategy_research_reports
from src.reports.strategy_report_trend import build_strategy_report_trend
from src.security.policy import get_security_policy
from src.workspace.workspace_service import create_workspace, ensure_default_workspace, get_user_workspaces, require_workspace_role
from live.pipeline import get_live_state
from runtime.monitoring_summary import build_monitoring_summary


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
        require_quota(auth_context.workspace_id, "report_generate", database_url=database_config.DATABASE_URL)
        report_request = ReportGenerateRequest(**(payload or {}))
        has_explicit_auth = bool(request.headers.get("X-Session-ID") or request.headers.get("X-API-Key"))
        account_user_id = auth_context.user_id if has_explicit_auth else report_request.user_id
        account = create_account_context(account_user_id)
        strategy_name = report_request.strategy_name
        plugin_result = registry.run("report", {"user_id": account.user_id, "strategy_name": strategy_name})
        record_usage(auth_context.workspace_id, account.user_id, "report_generate", metadata={"strategy_name": strategy_name})
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
    def list_database_reports(request: Request, user_id: str = "default", workspace_id: str = "default", page: int = 1, page_size: int = 20) -> dict:
        started = perf_counter()
        auth_context = require_permission(request, "report:read")
        query = ReportListQuery(user_id=auth_context.user_id or user_id, page=page, page_size=page_size)
        account = create_account_context(auth_context.user_id)
        warning: list[str] = []
        try:
            require_quota(auth_context.workspace_id, "api_call", database_url=database_config.DATABASE_URL)
            workspace = auth_context.workspace_id or workspace_id
            report_items = StrategyReportRepository(database_config.DATABASE_URL).list_reports_by_user(account.user_id, workspace_id=workspace)
            reports = paginate_items(report_items, page=query.page, page_size=query.page_size)
        except Exception as exc:
            if isinstance(exc, ApiError) and exc.code == "QUOTA_EXCEEDED":
                raise
            reports = paginate_items([], page=query.page, page_size=query.page_size)
            warning = warning_from_exception("database unavailable", DatabaseApiError(str(exc)))
        try:
            record_usage(auth_context.workspace_id, account.user_id, "api_call", metadata={"endpoint": "/api/v2/reports/db-list"})
        except Exception:
            pass
        response = success_response(
            {"user": account.as_dict(), "workspace_id": auth_context.workspace_id, "reports": reports},
            started_at=started,
            warning=warning,
        )
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

    @api.get("/api/v2/system/liveness")
    def liveness() -> dict:
        started = perf_counter()
        response = success_response(
            {"status": "alive", "version": "V2.6", "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat()},
            started_at=started,
        )
        log_api_event("/api/v2/system/liveness", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/system/readiness")
    def readiness() -> dict:
        started = perf_counter()
        checks = {
            "database_ready": False,
            "auth_policy_ready": False,
            "workspace_ready": False,
            "quota_ready": False,
            "api_ready": True,
        }
        warning: list[str] = []
        try:
            initialize_database(database_config.DATABASE_URL)
            checks["database_ready"] = True
        except Exception as exc:
            warning.extend(warning_from_exception("database unavailable", DatabaseApiError(str(exc))))
        try:
            policy = get_security_policy()
            checks["auth_policy_ready"] = policy.auth_mode in {"local", "dev", "production"}
        except Exception as exc:
            warning.extend(warning_from_exception("auth policy unavailable", DatabaseApiError(str(exc))))
        try:
            WorkspaceRepository(database_config.DATABASE_URL).ensure_default_workspace("default")
            checks["workspace_ready"] = True
        except Exception as exc:
            warning.extend(warning_from_exception("workspace unavailable", DatabaseApiError(str(exc))))
        try:
            get_quota_status("default", database_url=database_config.DATABASE_URL)
            checks["quota_ready"] = True
        except Exception as exc:
            warning.extend(warning_from_exception("quota unavailable", DatabaseApiError(str(exc))))
        response = success_response({"readiness": checks, "ready": all(checks.values())}, started_at=started, warning=warning)
        log_api_event("/api/v2/system/readiness", "default", "ok", response["meta"]["latency_ms"], len(warning))
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

    @api.get("/api/v2/system/identity-plan")
    def identity_plan() -> dict:
        started = perf_counter()
        plan = get_identity_provider_plan()
        status = plan.status
        identity = {
            "mode": status.mode,
            "provider": status.current_provider,
            "production_ready": status.production_ready,
            "external_provider_enabled": status.external_provider_enabled,
            "warnings": list(status.warnings),
        }
        response = success_response({"identity": identity}, started_at=started, warning=identity["warnings"])
        log_api_event("/api/v2/system/identity-plan", "default", "ok", response["meta"]["latency_ms"], len(identity["warnings"]))
        return response

    @api.get("/api/v2/system/observability")
    def observability() -> dict:
        started = perf_counter()
        planning = observability_planning_status()
        record_health_snapshot("observability", "ok", warning_count=len(planning["warnings"]), error_count=0)
        observability_summary = {
            "mode": planning["mode"],
            "provider": planning["provider"],
            "external_provider_enabled": planning["external_provider_enabled"],
            "api_metrics": get_api_metrics_summary(),
            "health_timeline": get_health_timeline_summary(),
            "warnings": planning["warnings"],
        }
        response = success_response({"observability": observability_summary}, started_at=started, warning=planning["warnings"])
        log_api_event("/api/v2/system/observability", "default", "ok", response["meta"]["latency_ms"], len(planning["warnings"]))
        return response

    @api.get("/api/v2/system/deployment-dry-run")
    def deployment_dry_run() -> dict:
        started = perf_counter()
        deployment = deployment_planning_status()
        response = success_response({"deployment": deployment}, started_at=started, warning=deployment["warnings"])
        log_api_event("/api/v2/system/deployment-dry-run", "default", "ok", response["meta"]["latency_ms"], len(deployment["warnings"]))
        return response

    @api.get("/api/v2/system/v3-release-candidate")
    def v3_release_candidate() -> dict:
        started = perf_counter()
        release_candidate = {
            "version": "V3.6",
            "scope": "product_demo_freeze",
            "demo_ready": True,
            "external_services_connected": False,
            "broker_connected": False,
            "real_payment_enabled": False,
            "production_identity_enabled": False,
            "warnings": [],
        }
        response = success_response({"release_candidate": release_candidate}, started_at=started)
        log_api_event("/api/v2/system/v3-release-candidate", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/system/onboarding")
    def onboarding() -> dict:
        started = perf_counter()
        onboarding_summary = {
            "version": "V3.7",
            "mode": "demo",
            "first_run_ready": True,
            "recommended_steps": [
                "Open onboarding",
                "Open dashboard",
                "Use demo login",
                "Review admin console",
                "Read API docs",
            ],
            "safety_boundaries": [
                "Research mode only",
                "No broker connection",
                "No automated trading",
                "No real payment",
                "No production identity",
                "No external cloud connected",
                "No AI API connected",
            ],
            "external_services_connected": False,
            "warnings": [],
        }
        response = success_response({"onboarding": onboarding_summary}, started_at=started)
        log_api_event("/api/v2/system/onboarding", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/system/workspace-demo")
    def workspace_demo() -> dict:
        started = perf_counter()
        workspace_demo_summary = {
            "version": "V3.8",
            "mode": "demo",
            "workspace_name": "Demo Workspace",
            "plan": "demo",
            "roles": ["admin", "user", "viewer"],
            "quota": {
                "report_limit": "demo only",
                "api_limit": "demo only",
                "workspace_limit": 1,
            },
            "usage": {
                "reports_generated": 3,
                "api_requests": 12,
                "workspace_members": 3,
            },
            "reports": {
                "available": 3,
                "latest": "Release candidate summary",
                "storage": "demo archive",
            },
            "real_customer_connected": False,
            "real_billing_enabled": False,
            "broker_connected": False,
            "auto_trading_enabled": False,
            "warnings": [],
        }
        response = success_response({"workspace_demo": workspace_demo_summary}, started_at=started)
        log_api_event("/api/v2/system/workspace-demo", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/system/pricing-plan")
    def pricing_plan() -> dict:
        started = perf_counter()
        pricing = {
            "version": "V3.9",
            "billing_mode": "mock",
            "real_payment_enabled": False,
            "stripe_live_enabled": False,
            "commercial_ready": False,
            "plans": [
                {
                    "name": "Free Demo",
                    "status": "demo",
                    "price_label": "$0 demo",
                    "target_user": "evaluator",
                    "quota_concept": "small demo quota",
                    "workspace_concept": "single demo workspace",
                    "support_level": "self-guided docs",
                },
                {
                    "name": "Research Pro",
                    "status": "planned",
                    "price_label": "future package",
                    "target_user": "independent researcher",
                    "quota_concept": "planned larger research quota",
                    "workspace_concept": "one research workspace",
                    "support_level": "planned product support",
                },
                {
                    "name": "Team Workspace",
                    "status": "planned",
                    "price_label": "future package",
                    "target_user": "small research team",
                    "quota_concept": "planned team quota",
                    "workspace_concept": "shared team workspace",
                    "support_level": "planned team support",
                },
                {
                    "name": "Enterprise Planned",
                    "status": "planned",
                    "price_label": "future package",
                    "target_user": "enterprise buyer",
                    "quota_concept": "custom planned quota",
                    "workspace_concept": "multi-workspace structure",
                    "support_level": "planned enterprise support",
                },
            ],
            "warnings": [],
        }
        response = success_response({"pricing": pricing}, started_at=started)
        log_api_event("/api/v2/system/pricing-plan", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/system/production-readiness")
    def production_readiness() -> dict:
        started = perf_counter()
        production_readiness_summary = {
            "version": "V4.0",
            "demo_ready": True,
            "production_ready": False,
            "blocking_items": [
                "production identity provider not connected",
                "production database not connected",
                "production cloud deployment not connected",
                "real payment not connected",
                "monitoring provider not connected",
                "legal/compliance docs not complete",
                "broker integration intentionally disabled",
            ],
            "ready_items": [
                "UI shell",
                "Admin Console",
                "Demo auth",
                "Workspace demo",
                "Pricing demo",
                "Observability local",
                "Deployment dry run",
                "Release candidate checks",
            ],
            "external_services_connected": False,
            "broker_connected": False,
            "real_payment_enabled": False,
            "production_identity_enabled": False,
            "warnings": [],
        }
        response = success_response({"production_readiness": production_readiness_summary}, started_at=started)
        log_api_event("/api/v2/system/production-readiness", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/system/production-database")
    def production_database() -> dict:
        from src.db.production_database_plan import get_production_database_plan

        started = perf_counter()
        plan = get_production_database_plan()
        production_database_summary = {
            "current_database": plan["current_database"],
            "future_database": plan["future_database"],
            "production_enabled": plan["production_enabled"],
            "migration_ready": plan["migration_ready"],
            "external_database_connected": plan["external_database_connected"],
            "backup_policy_ready": plan["backup_policy_ready"],
            "rollback_policy_ready": plan["rollback_policy_ready"],
            "warnings": plan["warnings"],
        }
        response = success_response({"production_database": production_database_summary}, started_at=started)
        log_api_event("/api/v2/system/production-database", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/system/identity-integration")
    def identity_integration() -> dict:
        from src.auth.production_identity_plan import get_production_identity_integration_plan

        started = perf_counter()
        plan = get_production_identity_integration_plan()
        identity_integration_summary = {
            "current_identity": plan["current_identity"],
            "future_identity": plan["future_identity"],
            "production_identity_enabled": plan["production_identity_enabled"],
            "external_identity_connected": plan["external_identity_connected"],
            "external_identity_mapping_ready": plan["external_identity_mapping_ready"],
            "production_session_lifecycle_ready": plan["production_session_lifecycle_ready"],
            "auth_audit_ready": plan["auth_audit_ready"],
            "warnings": plan["warnings"],
        }
        response = success_response({"identity_integration": identity_integration_summary}, started_at=started)
        log_api_event("/api/v2/system/identity-integration", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/system/deployment-target")
    def deployment_target() -> dict:
        from src.deployment.deployment_target_plan import get_deployment_target_plan

        started = perf_counter()
        plan = get_deployment_target_plan()
        deployment_target_summary = {
            "current_state": plan["current_state"],
            "frontend_target": plan["frontend_target"],
            "backend_target": plan["backend_target"],
            "database_target": plan["database_target"],
            "secrets_target": plan["secrets_target"],
            "monitoring_target": plan["monitoring_target"],
            "production_deployment_enabled": plan["production_deployment_enabled"],
            "external_cloud_connected": plan["external_cloud_connected"],
            "warnings": plan["warnings"],
        }
        response = success_response({"deployment_target": deployment_target_summary}, started_at=started)
        log_api_event("/api/v2/system/deployment-target", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/system/workspace-health")
    def workspace_health() -> dict:
        started = perf_counter()
        try:
            repo = WorkspaceRepository(database_config.DATABASE_URL)
            default_workspace = repo.ensure_default_workspace("default")
            workspace_count = len(repo.list_workspaces_by_user("default"))
            workspace = {
                "default_workspace_ready": bool(default_workspace),
                "workspace_isolation_enabled": True,
                "workspace_count": workspace_count,
                "warnings": [],
            }
            warning: list[str] = []
        except Exception as exc:
            warning = warning_from_exception("workspace unavailable", DatabaseApiError(str(exc)))
            workspace = {
                "default_workspace_ready": False,
                "workspace_isolation_enabled": True,
                "workspace_count": 0,
                "warnings": warning,
            }
        response = success_response({"workspace": workspace}, started_at=started, warning=warning)
        log_api_event("/api/v2/system/workspace-health", "default", "ok", response["meta"]["latency_ms"], len(warning))
        return response

    @api.get("/api/v2/system/billing-health")
    def billing_health() -> dict:
        started = perf_counter()
        billing = {
            "billing_mode": "mock",
            "real_payment_enabled": False,
            "plans_ready": True,
            "usage_tracking_ready": True,
            "quota_enforcement_ready": True,
            "warnings": [],
        }
        response = success_response({"billing": billing}, started_at=started)
        log_api_event("/api/v2/system/billing-health", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.post("/api/v2/auth/login")
    def auth_login(payload: dict | None = None) -> dict:
        started = perf_counter()
        policy = get_security_policy()
        payload = payload or {}
        user_id = str(payload.get("user_id") or "default")
        role = str(payload.get("role") or "admin")
        user = set_user_role(user_id, role)
        ensure_default_workspace(user["user_id"], database_url=database_config.DATABASE_URL)
        session = create_session(user["user_id"], metadata={"role": user["role"]})
        session["role"] = user["role"]
        record_usage("default", user["user_id"], "auth_login", metadata={"auth_mode": policy.auth_mode})
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

    @api.get("/api/v2/workspaces")
    def list_workspaces(request: Request, user_id: str = "default") -> dict:
        started = perf_counter()
        auth_context = build_auth_context(request)
        account_user = auth_context.user_id or user_id
        workspaces = get_user_workspaces(account_user, database_url=database_config.DATABASE_URL)
        response = success_response({"user_id": account_user, "workspaces": workspaces}, started_at=started)
        log_api_event("/api/v2/workspaces", account_user, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/billing/plan")
    def billing_plan(request: Request) -> dict:
        started = perf_counter()
        auth_context = build_auth_context(request)
        plan = get_workspace_plan(auth_context.workspace_id, database_url=database_config.DATABASE_URL)
        response = success_response({"plan": plan}, started_at=started)
        log_api_event("/api/v2/billing/plan", auth_context.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/billing/quota")
    def billing_quota(request: Request) -> dict:
        started = perf_counter()
        auth_context = build_auth_context(request)
        quota = get_quota_status(auth_context.workspace_id, database_url=database_config.DATABASE_URL)
        response = success_response({"quota": quota}, started_at=started)
        log_api_event("/api/v2/billing/quota", auth_context.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.post("/api/v2/workspaces")
    def create_workspace_endpoint(request: Request, payload: dict | None = None) -> dict:
        started = perf_counter()
        policy = get_security_policy()
        payload = payload or {}
        if policy.auth_mode == "production":
            auth_context = require_permission(request, "admin:read")
            require_workspace_role(
                auth_context.user_id,
                auth_context.workspace_id,
                {"owner", "admin"},
                database_url=database_config.DATABASE_URL,
            )
            owner_user_id = auth_context.user_id
        else:
            owner_user_id = str(payload.get("owner_user_id") or request.query_params.get("user_id") or "default")
        workspace = create_workspace(
            owner_user_id=owner_user_id,
            name=str(payload.get("name") or payload.get("workspace_id") or "Workspace"),
            workspace_id=payload.get("workspace_id"),
            database_url=database_config.DATABASE_URL,
        )
        audit_auth_event(owner_user_id, "workspace.create", {"workspace_id": workspace["workspace_id"], "name": workspace["name"]})
        response = success_response({"workspace": workspace}, started_at=started)
        log_api_event("/api/v2/workspaces", owner_user_id, "ok", response["meta"]["latency_ms"])
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
        require_quota(auth_context.workspace_id, "api_call", database_url=database_config.DATABASE_URL)
        query = UserQuery(user_id=auth_context.user_id or user_id)
        account = create_account_context(query.user_id)
        plugin_result = registry.run("risk", {"user_id": account.user_id, "workspace_id": auth_context.workspace_id})
        record_usage(auth_context.workspace_id, account.user_id, "api_call", metadata={"endpoint": "/api/v2/risk"})
        response = success_response({"user": account.as_dict(), "workspace_id": auth_context.workspace_id, "risk": plugin_result}, started_at=started)
        log_api_event("/api/v2/risk", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/dashboard/summary")
    def dashboard_summary(request: Request, user_id: str = "default") -> dict:
        started = perf_counter()
        auth_context = require_permission(request, "dashboard:read")
        require_quota(auth_context.workspace_id, "api_call", database_url=database_config.DATABASE_URL)
        query = UserQuery(user_id=auth_context.user_id or user_id)
        account = create_account_context(query.user_id)
        dashboard = build_strategy_research_dashboard([])
        cache.set_dashboard(account.dashboard_path("summary").as_posix(), dashboard)
        record_usage(auth_context.workspace_id, account.user_id, "api_call", metadata={"endpoint": "/api/v2/dashboard/summary"})
        response = success_response({"user": account.as_dict(), "workspace_id": auth_context.workspace_id, "dashboard": dashboard}, started_at=started)
        log_api_event("/api/v2/dashboard/summary", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/admin/system")
    def system_admin(request: Request, user_id: str = "default") -> dict:
        started = perf_counter()
        auth_context = require_permission(request, "admin:read")
        require_quota(auth_context.workspace_id, "api_call", database_url=database_config.DATABASE_URL)
        query = UserQuery(user_id=auth_context.user_id or user_id)
        account = create_account_context(query.user_id)
        admin_panel = build_system_admin_panel(cache=cache, registry=registry)
        record_usage(auth_context.workspace_id, account.user_id, "api_call", metadata={"endpoint": "/api/v2/admin/system"})
        response = success_response({"user": account.as_dict(), "workspace_id": auth_context.workspace_id, "admin": admin_panel}, started_at=started)
        log_api_event("/api/v2/admin/system", account.user_id, "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v2/admin/console")
    def admin_console(request: Request) -> dict:
        started = perf_counter()
        auth_context = require_permission(request, "admin:read")
        summary = build_admin_console_summary()
        response = success_response({"admin_console": summary}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v2/admin/console", auth_context.user_id, "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    @api.get("/api/v5/live_status")
    def v5_live_status() -> dict:
        started = perf_counter()
        state = get_live_state()
        response = success_response(
            {
                "live_status": {
                    "status": state["status"],
                    "safety": state["safety"],
                    "monitoring": state["monitoring"],
                }
            },
            started_at=started,
        )
        log_api_event("/api/v5/live_status", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/pnl")
    def v5_pnl() -> dict:
        started = perf_counter()
        state = get_live_state()
        response = success_response(
            {
                "pnl": {
                    "portfolio": state["portfolio"],
                    "equity_curve": state["monitoring"]["equity_curve"],
                    "drawdown_curve": state["monitoring"]["drawdown_curve"],
                    "exposure_curve": state["monitoring"]["exposure_curve"],
                }
            },
            started_at=started,
        )
        log_api_event("/api/v5/pnl", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/positions")
    def v5_positions() -> dict:
        started = perf_counter()
        state = get_live_state()
        response = success_response({"positions": state["positions"]}, started_at=started)
        log_api_event("/api/v5/positions", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/signals")
    def v5_signals() -> dict:
        started = perf_counter()
        state = get_live_state()
        response = success_response({"signals": state["signals"]}, started_at=started)
        log_api_event("/api/v5/signals", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/monitoring/summary")
    def v5_monitoring_summary() -> dict:
        started = perf_counter()
        summary = build_monitoring_summary()
        response = success_response({"monitoring": summary}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v5/monitoring/summary", "default", "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    @api.get("/api/v5/monitoring/pnl")
    def v5_monitoring_pnl() -> dict:
        started = perf_counter()
        summary = build_monitoring_summary()
        response = success_response(
            {
                "pnl": {
                    "paper_trading": True,
                    "real_trading": False,
                    "broker_connected": False,
                    "latest_equity": summary["latest_equity"],
                    "cash": summary["cash"],
                    "position_value": summary["position_value"],
                }
            },
            started_at=started,
            warning=summary.get("warnings", []),
        )
        log_api_event("/api/v5/monitoring/pnl", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/monitoring/positions")
    def v5_monitoring_positions() -> dict:
        started = perf_counter()
        summary = build_monitoring_summary()
        response = success_response(
            {"positions": summary["open_positions"], "paper_trading": True, "real_trading": False, "broker_connected": False},
            started_at=started,
            warning=summary.get("warnings", []),
        )
        log_api_event("/api/v5/monitoring/positions", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/monitoring/signals")
    def v5_monitoring_signals() -> dict:
        started = perf_counter()
        summary = build_monitoring_summary()
        response = success_response(
            {"signals": summary["recent_signals"], "paper_trading": True, "real_trading": False, "broker_connected": False},
            started_at=started,
            warning=summary.get("warnings", []),
        )
        log_api_event("/api/v5/monitoring/signals", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/monitoring/trades")
    def v5_monitoring_trades() -> dict:
        started = perf_counter()
        summary = build_monitoring_summary()
        response = success_response(
            {"trades": summary["recent_trades"], "paper_trading": True, "real_trading": False, "broker_connected": False},
            started_at=started,
            warning=summary.get("warnings", []),
        )
        log_api_event("/api/v5/monitoring/trades", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/monitoring/errors")
    def v5_monitoring_errors() -> dict:
        started = perf_counter()
        summary = build_monitoring_summary()
        response = success_response(
            {"errors": summary["recent_errors"], "paper_trading": True, "real_trading": False, "broker_connected": False},
            started_at=started,
            warning=summary.get("warnings", []),
        )
        log_api_event("/api/v5/monitoring/errors", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/monitoring/health")
    def v5_monitoring_health() -> dict:
        started = perf_counter()
        summary = build_monitoring_summary()
        response = success_response(
            {"health": summary["health"], "status": summary["status"], "paper_trading": True, "real_trading": False, "broker_connected": False},
            started_at=started,
            warning=summary.get("warnings", []),
        )
        log_api_event("/api/v5/monitoring/health", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/monitoring/risk")
    def v5_monitoring_risk() -> dict:
        started = perf_counter()
        summary = build_monitoring_summary()
        response = success_response(
            {"risk": summary["risk"], "mode": summary["mode"], "paper_trading": True, "real_trading": False, "broker_connected": False},
            started_at=started,
            warning=summary.get("warnings", []),
        )
        log_api_event("/api/v5/monitoring/risk", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/monitoring/soak-report")
    def v5_monitoring_soak_report() -> dict:
        started = perf_counter()
        summary = build_monitoring_summary()
        response = success_response(
            {"soak_report": summary["soak_report"], "paper_trading": True, "real_trading": False, "broker_connected": False},
            started_at=started,
            warning=summary.get("warnings", []),
        )
        log_api_event("/api/v5/monitoring/soak-report", "default", "ok", response["meta"]["latency_ms"])
        return response

    return api


app = create_v2_api_app()

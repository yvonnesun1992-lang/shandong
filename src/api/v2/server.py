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
from scripts.v55_deployment_dry_run_check import build_v55_deployment_payload
from config.v5_live_data_config import get_live_data_status
from runtime.live_market_data import build_live_market_data_adapter
from runtime.live_data_normalizer import normalize_live_ticks
from runtime.live_paper_staging_runner import run_live_paper_staging
from runtime.live_paper_alpha_runner import run_live_paper_alpha_staging
from broker.broker_integration_report import build_broker_integration_summary
from broker.broker_safety_gate import broker_readiness_summary, validate_broker_safety
from broker.order_mapping_plan import build_order_mapping_plan
from config.v5_broker_integration_config import get_broker_integration_status
from approval.approval_audit_trail import build_approval_audit_summary
from approval.manual_approval_gate import approval_readiness_summary
from approval.manual_approval_report import build_manual_approval_summary
from config.v5_manual_approval_config import get_manual_approval_policy, get_manual_approval_status
from config.v5_broker_sandbox_config import get_sandbox_readiness_status
from sandbox.credential_isolation_plan import build_credential_isolation_plan
from sandbox.sandbox_order_lifecycle_plan import build_sandbox_order_lifecycle_plan
from sandbox.sandbox_provider_plan import build_sandbox_provider_plan, list_sandbox_provider_plans
from sandbox.sandbox_readiness_report import build_sandbox_readiness_summary
from sandbox.sandbox_rollback_plan import build_sandbox_rollback_plan
from sandbox.sandbox_safety_checklist import build_sandbox_safety_checklist
from config.v5_sandbox_simulation_config import get_sandbox_simulation_status
from sandbox_sim.sandbox_simulation_broker import SUPPORTED_SCENARIOS, SandboxSimulationBroker
from sandbox_sim.sandbox_simulation_report import build_sandbox_simulation_summary
from sandbox_sim.sandbox_simulation_runner import run_sandbox_simulation_session
from config.v5_sandbox_robustness_config import get_sandbox_robustness_status
from sandbox_sim.fault_combination_runner import run_all_fault_combinations
from sandbox_sim.long_run_robustness_runner import run_long_run_robustness
from sandbox_sim.multi_symbol_simulator import run_multi_symbol_simulation
from sandbox_sim.robustness_scenario_matrix import build_robustness_scenario_matrix
from sandbox_sim.sandbox_robustness_report import build_sandbox_robustness_summary
from config.v5_sandbox_connector_contract_config import get_connector_contract_status
from config.v5_sandbox_connector_mock_config import get_mock_connector_status
from sandbox_connector.connector_interface_contract import build_interface_contract
from sandbox_connector.connector_safety_validator import build_connector_readiness_summary
from sandbox_connector.credential_boundary_contract import build_credential_boundary_contract
from sandbox_connector.error_code_contract import list_error_codes
from sandbox_connector.idempotency_policy import build_idempotency_policy
from sandbox_connector.mock_connector_report import build_mock_connector_summary
from sandbox_connector.mock_connector_safety_validator import validate_mock_connector_safety
from sandbox_connector.mock_connector_scenario_runner import run_all_mock_connector_scenarios
from sandbox_connector.mock_sandbox_connector import MockSandboxConnector
from sandbox_connector.rate_limit_policy import build_rate_limit_policy
from sandbox_connector.request_schema_contract import build_request_schema_contract
from sandbox_connector.response_schema_contract import build_response_schema_contract
from sandbox_connector.retry_policy import build_retry_policy
from broker_adapter.adapter_factory import build_factory_status
from broker_adapter.adapter_registry import build_default_registry
from broker_adapter.broker_adapter_report import build_broker_adapter_summary
from broker_adapter.capability_matrix import build_capability_matrix
from broker_adapter.compatibility_layer import validate_contract_alignment, validate_interface_compatibility
from broker_adapter.safety_guard import build_safety_guard_status
from sandbox_bridge.bridge_safety_gate import validate_bridge_safety
from sandbox_bridge.error_translation_layer import translate_error
from sandbox_bridge.idempotency_enforcer import IdempotencyEnforcer
from sandbox_bridge.request_transformer import transform_submit_order
from sandbox_bridge.response_normalizer import normalize_order_response
from sandbox_bridge.retry_orchestrator import schedule_retry
from sandbox_bridge.sandbox_bridge_core import SandboxBridgeCore
from sandbox_bridge.sandbox_bridge_report import build_sandbox_bridge_summary
from sandbox_bridge.sandbox_router import route_request
from sandbox_bridge.sandbox_session import SandboxSession
from integration_test.integration_scenario_matrix import build_integration_scenario_matrix
from integration_test.integration_test_core import IntegrationTestCore
from integration_test.integration_test_orchestrator import run_all_tests, run_scenario, summarize_results
from integration_test.integration_test_report import build_integration_test_summary


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

    @api.get("/api/v5/deployment/dry-run")
    def v5_deployment_dry_run() -> dict:
        started = perf_counter()
        deployment = build_v55_deployment_payload()
        response = success_response({"deployment": deployment}, started_at=started, warning=deployment.get("warnings", []))
        log_api_event("/api/v5/deployment/dry-run", "default", "ok", response["meta"]["latency_ms"], len(deployment.get("warnings", [])))
        return response

    @api.get("/api/v5/deployment/readiness")
    def v5_deployment_readiness() -> dict:
        started = perf_counter()
        deployment = build_v55_deployment_payload()
        response = success_response({"deployment": deployment}, started_at=started, warning=deployment.get("warnings", []))
        log_api_event("/api/v5/deployment/readiness", "default", "ok", response["meta"]["latency_ms"], len(deployment.get("warnings", [])))
        return response

    @api.get("/api/v5/live-paper/status")
    def v5_live_paper_status() -> dict:
        started = perf_counter()
        status = get_live_data_status()
        response = success_response({"live_paper": status}, started_at=started)
        log_api_event("/api/v5/live-paper/status", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/live-paper/config")
    def v5_live_paper_config() -> dict:
        started = perf_counter()
        status = get_live_data_status()
        response = success_response({"config": status}, started_at=started)
        log_api_event("/api/v5/live-paper/config", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/live-paper/latest-tick")
    def v5_live_paper_latest_tick() -> dict:
        started = perf_counter()
        status = get_live_data_status()
        adapter = build_live_market_data_adapter(status["live_data_mode"], status["symbols"])
        normalized = normalize_live_ticks(adapter.get_latest_ticks())
        latest_tick = normalized["valid_ticks"][-1] if normalized["valid_ticks"] else {}
        data = {
            "latest_tick": latest_tick,
            "paper_trading": True,
            "real_trading": False,
            "broker_connected": False,
            "real_money_enabled": False,
            "warnings": [item.get("reason", "invalid tick") for item in normalized["invalid_ticks"]],
        }
        response = success_response(data, started_at=started, warning=data["warnings"])
        log_api_event("/api/v5/live-paper/latest-tick", "default", "ok", response["meta"]["latency_ms"], len(data["warnings"]))
        return response

    @api.get("/api/v5/live-paper/summary")
    def v5_live_paper_summary() -> dict:
        started = perf_counter()
        status = get_live_data_status()
        summary = run_live_paper_staging(mode=status["live_data_mode"], max_ticks=1, dry_run_once=True)
        response = success_response({"summary": summary}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v5/live-paper/summary", "default", "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    @api.get("/api/v5/live-alpha/status")
    def v5_live_alpha_status() -> dict:
        started = perf_counter()
        status = get_live_data_status()
        payload = {
            "version": "V5.7",
            "mode": status["live_data_mode"],
            "symbols": status["symbols"],
            "alpha_signal_driven": True,
            "paper_trading": True,
            "real_trading": False,
            "broker_connected": False,
            "real_money_enabled": False,
        }
        response = success_response({"live_alpha": payload}, started_at=started)
        log_api_event("/api/v5/live-alpha/status", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/live-alpha/latest-signals")
    def v5_live_alpha_latest_signals() -> dict:
        started = perf_counter()
        status = get_live_data_status()
        summary = run_live_paper_alpha_staging(mode=status["live_data_mode"], max_ticks=3)
        response = success_response({"signals": summary["latest_signals"], "paper_trading": True, "real_trading": False, "broker_connected": False}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v5/live-alpha/latest-signals", "default", "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    @api.get("/api/v5/live-alpha/summary")
    def v5_live_alpha_summary() -> dict:
        started = perf_counter()
        status = get_live_data_status()
        summary = run_live_paper_alpha_staging(mode=status["live_data_mode"], max_ticks=10)
        response = success_response({"summary": summary}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v5/live-alpha/summary", "default", "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    @api.get("/api/v5/live-alpha/buffer-status")
    def v5_live_alpha_buffer_status() -> dict:
        started = perf_counter()
        status = get_live_data_status()
        summary = run_live_paper_alpha_staging(mode=status["live_data_mode"], max_ticks=5)
        response = success_response({"buffer_status": summary["buffer_status"], "paper_trading": True, "real_trading": False, "broker_connected": False}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v5/live-alpha/buffer-status", "default", "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    @api.get("/api/v5/broker/status")
    def v5_broker_status() -> dict:
        started = perf_counter()
        status = get_broker_integration_status()
        response = success_response({"broker": status}, started_at=started, warning=status.get("warning", []))
        log_api_event("/api/v5/broker/status", "default", "ok", response["meta"]["latency_ms"], len(status.get("warning", [])))
        return response

    @api.get("/api/v5/broker/readiness")
    def v5_broker_readiness() -> dict:
        started = perf_counter()
        summary = build_broker_integration_summary()
        response = success_response({"readiness": summary}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v5/broker/readiness", "default", "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    @api.get("/api/v5/broker/safety")
    def v5_broker_safety() -> dict:
        started = perf_counter()
        safety = validate_broker_safety()
        readiness = broker_readiness_summary()
        response = success_response({"safety": safety, "readiness": readiness}, started_at=started, warning=safety.get("warnings", []))
        log_api_event("/api/v5/broker/safety", "default", "ok", response["meta"]["latency_ms"], len(safety.get("warnings", [])))
        return response

    @api.get("/api/v5/broker/order-mapping")
    def v5_broker_order_mapping() -> dict:
        started = perf_counter()
        mapping = build_order_mapping_plan()
        response = success_response({"order_mapping": mapping}, started_at=started, warning=mapping.get("warnings", []))
        log_api_event("/api/v5/broker/order-mapping", "default", "ok", response["meta"]["latency_ms"], len(mapping.get("warnings", [])))
        return response

    @api.get("/api/v5/approval/status")
    def v5_approval_status() -> dict:
        started = perf_counter()
        status = get_manual_approval_status()
        response = success_response({"approval": status}, started_at=started, warning=status.get("warning", []))
        log_api_event("/api/v5/approval/status", "default", "ok", response["meta"]["latency_ms"], len(status.get("warning", [])))
        return response

    @api.get("/api/v5/approval/readiness")
    def v5_approval_readiness() -> dict:
        started = perf_counter()
        summary = build_manual_approval_summary()
        response = success_response({"readiness": summary}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v5/approval/readiness", "default", "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    @api.get("/api/v5/approval/policy")
    def v5_approval_policy() -> dict:
        started = perf_counter()
        policy = get_manual_approval_policy()
        readiness = approval_readiness_summary()
        response = success_response({"policy": policy, "readiness": readiness}, started_at=started)
        log_api_event("/api/v5/approval/policy", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/approval/audit-summary")
    def v5_approval_audit_summary() -> dict:
        started = perf_counter()
        summary = build_approval_audit_summary()
        payload = {**summary, "manual_approval_required": True, "auto_approval_enabled": False, "real_orders_enabled": False, "real_money_enabled": False, "paper_trading": True}
        response = success_response({"audit_summary": payload}, started_at=started)
        log_api_event("/api/v5/approval/audit-summary", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox/status")
    def v5_sandbox_status() -> dict:
        started = perf_counter()
        status = get_sandbox_readiness_status()
        response = success_response({"sandbox": status}, started_at=started, warning=status.get("warning", []))
        log_api_event("/api/v5/sandbox/status", "default", "ok", response["meta"]["latency_ms"], len(status.get("warning", [])))
        return response

    @api.get("/api/v5/sandbox/provider-plan")
    def v5_sandbox_provider_plan() -> dict:
        started = perf_counter()
        status = get_sandbox_readiness_status()
        plan = build_sandbox_provider_plan(status["sandbox_provider"])
        response = success_response({"provider_plan": plan, "all_provider_plans": list_sandbox_provider_plans()}, started_at=started, warning=plan.get("warnings", []))
        log_api_event("/api/v5/sandbox/provider-plan", "default", "ok", response["meta"]["latency_ms"], len(plan.get("warnings", [])))
        return response

    @api.get("/api/v5/sandbox/credential-policy")
    def v5_sandbox_credential_policy() -> dict:
        started = perf_counter()
        policy = build_credential_isolation_plan()
        response = success_response({"credential_policy": policy}, started_at=started)
        log_api_event("/api/v5/sandbox/credential-policy", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox/order-lifecycle")
    def v5_sandbox_order_lifecycle() -> dict:
        started = perf_counter()
        lifecycle = build_sandbox_order_lifecycle_plan()
        response = success_response({"order_lifecycle": lifecycle}, started_at=started, warning=lifecycle.get("warnings", []))
        log_api_event("/api/v5/sandbox/order-lifecycle", "default", "ok", response["meta"]["latency_ms"], len(lifecycle.get("warnings", [])))
        return response

    @api.get("/api/v5/sandbox/safety-checklist")
    def v5_sandbox_safety_checklist() -> dict:
        started = perf_counter()
        checklist = build_sandbox_safety_checklist()
        response = success_response({"safety_checklist": checklist}, started_at=started, warning=checklist.get("warnings", []))
        log_api_event("/api/v5/sandbox/safety-checklist", "default", "ok", response["meta"]["latency_ms"], len(checklist.get("warnings", [])))
        return response

    @api.get("/api/v5/sandbox/rollback-plan")
    def v5_sandbox_rollback_plan() -> dict:
        started = perf_counter()
        rollback = build_sandbox_rollback_plan()
        response = success_response({"rollback_plan": rollback, "readiness": build_sandbox_readiness_summary()}, started_at=started, warning=rollback.get("warnings", []))
        log_api_event("/api/v5/sandbox/rollback-plan", "default", "ok", response["meta"]["latency_ms"], len(rollback.get("warnings", [])))
        return response

    @api.get("/api/v5/sandbox-sim/status")
    def v5_sandbox_sim_status() -> dict:
        started = perf_counter()
        status = get_sandbox_simulation_status()
        response = success_response({"sandbox_simulation": status}, started_at=started, warning=status.get("warnings", []))
        log_api_event("/api/v5/sandbox-sim/status", "default", "ok", response["meta"]["latency_ms"], len(status.get("warnings", [])))
        return response

    @api.get("/api/v5/sandbox-sim/account")
    def v5_sandbox_sim_account() -> dict:
        started = perf_counter()
        broker = SandboxSimulationBroker()
        broker.submit_order({"symbol": "AAPL", "side": "BUY", "quantity": 1})
        broker.step_market({"symbol": "AAPL", "price": 100.0})
        payload = {"account": broker.get_account(), "positions": broker.get_positions(), **_sandbox_sim_boundary()}
        response = success_response(payload, started_at=started)
        log_api_event("/api/v5/sandbox-sim/account", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-sim/orders")
    def v5_sandbox_sim_orders() -> dict:
        started = perf_counter()
        run = run_sandbox_simulation_session(scenario="partial_fill", max_ticks=2)
        response = success_response({"orders": run["orders"], **_sandbox_sim_boundary()}, started_at=started, warning=run.get("warnings", []))
        log_api_event("/api/v5/sandbox-sim/orders", "default", "ok", response["meta"]["latency_ms"], len(run.get("warnings", [])))
        return response

    @api.get("/api/v5/sandbox-sim/fills")
    def v5_sandbox_sim_fills() -> dict:
        started = perf_counter()
        run = run_sandbox_simulation_session(scenario="full_fill", max_ticks=2)
        response = success_response({"fills": run["fills"], **_sandbox_sim_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-sim/fills", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-sim/scenarios")
    def v5_sandbox_sim_scenarios() -> dict:
        started = perf_counter()
        response = success_response({"scenarios": SUPPORTED_SCENARIOS, **_sandbox_sim_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-sim/scenarios", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-sim/summary")
    def v5_sandbox_sim_summary(scenario: str = "full_fill", ticks: int = 10) -> dict:
        started = perf_counter()
        summary = build_sandbox_simulation_summary(scenario=scenario, max_ticks=min(max(ticks, 1), 100))
        response = success_response({"sandbox_simulation": summary, **_sandbox_sim_boundary()}, started_at=started, warning=summary["summary"].get("warnings", []))
        log_api_event("/api/v5/sandbox-sim/summary", "default", "ok", response["meta"]["latency_ms"], len(summary["summary"].get("warnings", [])))
        return response

    @api.get("/api/v5/sandbox-robustness/status")
    def v5_sandbox_robustness_status() -> dict:
        started = perf_counter()
        status = get_sandbox_robustness_status()
        response = success_response({"sandbox_robustness": status}, started_at=started)
        log_api_event("/api/v5/sandbox-robustness/status", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-robustness/scenario-matrix")
    def v5_sandbox_robustness_scenario_matrix() -> dict:
        started = perf_counter()
        matrix = build_robustness_scenario_matrix()
        response = success_response({"scenario_matrix": matrix, **_sandbox_sim_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-robustness/scenario-matrix", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-robustness/multi-symbol")
    def v5_sandbox_robustness_multi_symbol(ticks: int = 20) -> dict:
        started = perf_counter()
        result = run_multi_symbol_simulation(ticks=min(max(ticks, 1), 100), seed=42)
        response = success_response({"multi_symbol": result, **_sandbox_sim_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-robustness/multi-symbol", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-robustness/fault-combinations")
    def v5_sandbox_robustness_fault_combinations(ticks: int = 20) -> dict:
        started = perf_counter()
        result = run_all_fault_combinations(ticks=min(max(ticks, 1), 100), seed=42)
        response = success_response({"fault_combinations": result, **_sandbox_sim_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-robustness/fault-combinations", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-robustness/long-run")
    def v5_sandbox_robustness_long_run(ticks: int = 1000) -> dict:
        started = perf_counter()
        result = run_long_run_robustness(ticks=min(max(ticks, 1), 1000), scenarios=["full_fill", "reject"], seed=42)
        response = success_response({"long_run": result, **_sandbox_sim_boundary()}, started_at=started, warning=[] if result["final_verdict"] == "PASS" else ["local robustness warning scenarios present"])
        log_api_event("/api/v5/sandbox-robustness/long-run", "default", "ok", response["meta"]["latency_ms"], 0 if result["final_verdict"] == "PASS" else 1)
        return response

    @api.get("/api/v5/sandbox-robustness/summary")
    def v5_sandbox_robustness_summary(scenario: str = "full_fill", ticks: int = 100) -> dict:
        started = perf_counter()
        summary = build_sandbox_robustness_summary(scenario=scenario, ticks=min(max(ticks, 1), 1000), all_scenarios=False)
        response = success_response({"sandbox_robustness": summary, **_sandbox_sim_boundary()}, started_at=started, warning=[] if summary["verdict"] == "PASS" else ["local robustness warning scenarios present"])
        log_api_event("/api/v5/sandbox-robustness/summary", "default", "ok", response["meta"]["latency_ms"], 0 if summary["verdict"] == "PASS" else 1)
        return response

    @api.get("/api/v5/sandbox-connector/status")
    def v5_sandbox_connector_status() -> dict:
        started = perf_counter()
        status = get_connector_contract_status()
        response = success_response({"sandbox_connector": status}, started_at=started)
        log_api_event("/api/v5/sandbox-connector/status", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector/interface-contract")
    def v5_sandbox_connector_interface_contract() -> dict:
        started = perf_counter()
        response = success_response({"interface_contract": build_interface_contract(), **_connector_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-connector/interface-contract", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector/request-schema")
    def v5_sandbox_connector_request_schema() -> dict:
        started = perf_counter()
        response = success_response({"request_schema": build_request_schema_contract(), **_connector_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-connector/request-schema", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector/response-schema")
    def v5_sandbox_connector_response_schema() -> dict:
        started = perf_counter()
        response = success_response({"response_schema": build_response_schema_contract(), **_connector_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-connector/response-schema", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector/error-codes")
    def v5_sandbox_connector_error_codes() -> dict:
        started = perf_counter()
        response = success_response({"error_codes": list_error_codes(), **_connector_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-connector/error-codes", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector/idempotency")
    def v5_sandbox_connector_idempotency() -> dict:
        started = perf_counter()
        response = success_response({"idempotency": build_idempotency_policy(), **_connector_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-connector/idempotency", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector/rate-limit")
    def v5_sandbox_connector_rate_limit() -> dict:
        started = perf_counter()
        response = success_response({"rate_limit": build_rate_limit_policy(), **_connector_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-connector/rate-limit", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector/retry-policy")
    def v5_sandbox_connector_retry_policy() -> dict:
        started = perf_counter()
        response = success_response({"retry_policy": build_retry_policy(), **_connector_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-connector/retry-policy", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector/credential-boundary")
    def v5_sandbox_connector_credential_boundary() -> dict:
        started = perf_counter()
        response = success_response({"credential_boundary": build_credential_boundary_contract(), **_connector_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-connector/credential-boundary", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector/readiness")
    def v5_sandbox_connector_readiness() -> dict:
        started = perf_counter()
        readiness = build_connector_readiness_summary()
        response = success_response({"readiness": readiness, **_connector_boundary()}, started_at=started, warning=readiness.get("warnings", []))
        log_api_event("/api/v5/sandbox-connector/readiness", "default", "ok", response["meta"]["latency_ms"], len(readiness.get("warnings", [])))
        return response

    @api.get("/api/v5/sandbox-connector-mock/status")
    def v5_sandbox_connector_mock_status() -> dict:
        started = perf_counter()
        status = get_mock_connector_status()
        response = success_response({"sandbox_connector_mock": status, **_mock_connector_boundary()}, started_at=started, warning=status.get("warnings", []))
        log_api_event("/api/v5/sandbox-connector-mock/status", "default", "ok", response["meta"]["latency_ms"], len(status.get("warnings", [])))
        return response

    @api.get("/api/v5/sandbox-connector-mock/account")
    def v5_sandbox_connector_mock_account() -> dict:
        started = perf_counter()
        account = MockSandboxConnector().get_account()
        response = success_response({"account": account, **_mock_connector_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-connector-mock/account", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector-mock/positions")
    def v5_sandbox_connector_mock_positions() -> dict:
        started = perf_counter()
        positions = MockSandboxConnector().get_positions()
        response = success_response({"positions": positions, **_mock_connector_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-connector-mock/positions", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector-mock/recent-orders")
    def v5_sandbox_connector_mock_recent_orders() -> dict:
        started = perf_counter()
        connector = MockSandboxConnector()
        connector.submit_order({"client_order_id": "mock-client-api", "idempotency_key": "mock-idem-api", "symbol": "AAPL", "side": "BUY", "quantity": 1, "order_type": "MARKET", "created_at": datetime.now(UTC).replace(microsecond=0).isoformat()})
        orders = connector.get_recent_orders()
        response = success_response({"recent_orders": orders, **_mock_connector_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-connector-mock/recent-orders", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-connector-mock/scenarios")
    def v5_sandbox_connector_mock_scenarios() -> dict:
        started = perf_counter()
        scenarios = run_all_mock_connector_scenarios()
        response = success_response({"scenarios": scenarios, **_mock_connector_boundary()}, started_at=started, warning=[] if scenarios["summary"]["verdict"] == "PASS" else ["mock scenario warning"])
        log_api_event("/api/v5/sandbox-connector-mock/scenarios", "default", "ok", response["meta"]["latency_ms"], 0 if scenarios["summary"]["verdict"] == "PASS" else 1)
        return response

    @api.get("/api/v5/sandbox-connector-mock/safety")
    def v5_sandbox_connector_mock_safety() -> dict:
        started = perf_counter()
        safety = validate_mock_connector_safety()
        response = success_response({"safety": safety, **_mock_connector_boundary()}, started_at=started, warning=safety.get("warnings", []))
        log_api_event("/api/v5/sandbox-connector-mock/safety", "default", "ok", response["meta"]["latency_ms"], len(safety.get("warnings", [])))
        return response

    @api.get("/api/v5/sandbox-connector-mock/summary")
    def v5_sandbox_connector_mock_summary() -> dict:
        started = perf_counter()
        summary = build_mock_connector_summary(all_scenarios=True)
        response = success_response({"summary": summary, **_mock_connector_boundary()}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v5/sandbox-connector-mock/summary", "default", "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    @api.get("/api/v5/broker-adapter/list")
    def v5_broker_adapter_list() -> dict:
        started = perf_counter()
        registry = build_default_registry()
        response = success_response({"adapters": registry.list_adapters(), **_broker_adapter_boundary()}, started_at=started)
        log_api_event("/api/v5/broker-adapter/list", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/broker-adapter/capabilities")
    def v5_broker_adapter_capabilities() -> dict:
        started = perf_counter()
        matrix = build_capability_matrix()
        response = success_response({"capability_matrix": matrix, **_broker_adapter_boundary()}, started_at=started)
        log_api_event("/api/v5/broker-adapter/capabilities", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/broker-adapter/registry")
    def v5_broker_adapter_registry() -> dict:
        started = perf_counter()
        registry = build_default_registry()
        compatibility = validate_interface_compatibility()
        alignment = validate_contract_alignment()
        response = success_response({"registry": registry.as_dict(), "compatibility": compatibility, "alignment": alignment, **_broker_adapter_boundary()}, started_at=started)
        log_api_event("/api/v5/broker-adapter/registry", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/broker-adapter/factory")
    def v5_broker_adapter_factory(provider: str = "mock") -> dict:
        started = perf_counter()
        factory = build_factory_status(provider)
        response = success_response({"factory": factory, **_broker_adapter_boundary()}, started_at=started)
        log_api_event("/api/v5/broker-adapter/factory", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/broker-adapter/safety")
    def v5_broker_adapter_safety() -> dict:
        started = perf_counter()
        safety = build_safety_guard_status()
        summary = build_broker_adapter_summary()
        response = success_response({"safety": safety, "summary": summary, **_broker_adapter_boundary()}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v5/broker-adapter/safety", "default", "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    @api.get("/api/v5/sandbox-bridge/status")
    def v5_sandbox_bridge_status() -> dict:
        started = perf_counter()
        bridge = SandboxBridgeCore()
        response = success_response({"status": bridge.status(), **_sandbox_bridge_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-bridge/status", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-bridge/session")
    def v5_sandbox_bridge_session() -> dict:
        started = perf_counter()
        session = SandboxSession()
        response = success_response({"session": session.start_session(), **_sandbox_bridge_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-bridge/session", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-bridge/routing")
    def v5_sandbox_bridge_routing() -> dict:
        started = perf_counter()
        routing = route_request({"backend": "bridge", "symbol": "AAPL", "side": "BUY", "quantity": 1})
        response = success_response({"routing": routing, **_sandbox_bridge_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-bridge/routing", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-bridge/transform")
    def v5_sandbox_bridge_transform() -> dict:
        started = perf_counter()
        transformed = transform_submit_order({"symbol": "AAPL", "side": "BUY", "quantity": 1})
        response = success_response({"transform": transformed, **_sandbox_bridge_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-bridge/transform", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-bridge/normalize")
    def v5_sandbox_bridge_normalize() -> dict:
        started = perf_counter()
        normalized = normalize_order_response({"status": "accepted"})
        response = success_response({"normalize": normalized, **_sandbox_bridge_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-bridge/normalize", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-bridge/retry")
    def v5_sandbox_bridge_retry() -> dict:
        started = perf_counter()
        retry = schedule_retry("TIMEOUT", 1)
        error = translate_error({"type": "timeout"})
        response = success_response({"retry": retry, "error_translation": error, **_sandbox_bridge_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-bridge/retry", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-bridge/idempotency")
    def v5_sandbox_bridge_idempotency() -> dict:
        started = perf_counter()
        enforcer = IdempotencyEnforcer()
        request = {"symbol": "AAPL", "side": "BUY", "quantity": 1}
        enforcer.record_request(request, {"status": "MOCK_ACCEPTED"})
        response = success_response({"idempotency": enforcer.check_duplicate(request), **_sandbox_bridge_boundary()}, started_at=started)
        log_api_event("/api/v5/sandbox-bridge/idempotency", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/sandbox-bridge/safety")
    def v5_sandbox_bridge_safety() -> dict:
        started = perf_counter()
        safety = validate_bridge_safety({"bridge_only": True})
        summary = build_sandbox_bridge_summary()
        response = success_response({"safety": safety, "summary": summary, **_sandbox_bridge_boundary()}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v5/sandbox-bridge/safety", "default", "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    @api.get("/api/v5/integration-test/status")
    def v5_integration_test_status() -> dict:
        started = perf_counter()
        core = IntegrationTestCore(seed=42)
        status = core.run_full_pipeline_test()
        response = success_response({"status": status, **_integration_test_boundary()}, started_at=started)
        log_api_event("/api/v5/integration-test/status", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/integration-test/scenarios")
    def v5_integration_test_scenarios() -> dict:
        started = perf_counter()
        matrix = build_integration_scenario_matrix(seed=42)
        response = success_response({"scenarios": matrix, **_integration_test_boundary()}, started_at=started)
        log_api_event("/api/v5/integration-test/scenarios", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/integration-test/run")
    def v5_integration_test_run(scenario: str = "normal_flow") -> dict:
        started = perf_counter()
        result = run_scenario(scenario)
        response = success_response({"run": result, **_integration_test_boundary()}, started_at=started)
        log_api_event("/api/v5/integration-test/run", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/integration-test/layers")
    def v5_integration_test_layers() -> dict:
        started = perf_counter()
        layers = IntegrationTestCore(seed=42).run_layered_test()
        response = success_response({"layers": layers, **_integration_test_boundary()}, started_at=started)
        log_api_event("/api/v5/integration-test/layers", "default", "ok", response["meta"]["latency_ms"])
        return response

    @api.get("/api/v5/integration-test/summary")
    def v5_integration_test_summary() -> dict:
        started = perf_counter()
        results = run_all_tests()
        summary = build_integration_test_summary(all_scenarios=True)
        response = success_response({"summary": summary, "orchestrator": summarize_results(results), **_integration_test_boundary()}, started_at=started, warning=summary.get("warnings", []))
        log_api_event("/api/v5/integration-test/summary", "default", "ok", response["meta"]["latency_ms"], len(summary.get("warnings", [])))
        return response

    return api


app = create_v2_api_app()


def _sandbox_sim_boundary() -> dict:
    return {
        "simulation_only": True,
        "real_sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def _connector_boundary() -> dict:
    return {
        "contract_only": True,
        "connector_runtime_enabled": False,
        "real_sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def _mock_connector_boundary() -> dict:
    return {
        "mock_only": True,
        "real_connector_runtime_enabled": False,
        "real_sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def _broker_adapter_boundary() -> dict:
    return {
        "skeleton_only": True,
        "real_connection": False,
        "real_orders": False,
        "paper_trading": True,
    }


def _sandbox_bridge_boundary() -> dict:
    return {
        "bridge_only": True,
        "real_connection": False,
        "real_orders": False,
        "paper_trading": True,
    }


def _integration_test_boundary() -> dict:
    return {
        "integration_only": True,
        "simulation_only": True,
        "broker_connected": False,
        "real_orders_enabled": False,
        "paper_trading": True,
    }

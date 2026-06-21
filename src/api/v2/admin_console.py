from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from scripts.startup_check import run_startup_check
from src.billing.plan_service import get_workspace_plan
from src.billing.quota_service import get_quota_status
from src.config import database_config
from src.db.migrations import initialize_database
from src.db.repository import UserRepository
from src.db.workspace_repository import WorkspaceRepository
from src.security.policy import get_security_policy
from src.security.sanitizer import sanitize_response_payload
from src.system.health_check import run_system_health_check


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _database_type(database_url: str) -> str:
    if database_url.startswith("sqlite:///"):
        return "sqlite"
    if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
        return "postgresql"
    return "unknown"


def _sanitize(value):
    return sanitize_response_payload(value)


def _warning(prefix: str, exc: Exception) -> str:
    return f"{prefix}: {type(exc).__name__}"


def _safe_section(name: str, collector: Callable[[], dict]) -> tuple[dict, list[str]]:
    try:
        return _sanitize(collector()), []
    except Exception as exc:
        warning = _warning(f"{name} unavailable", exc)
        return {"status": "warning", "warnings": [warning]}, [warning]


def collect_system_health() -> dict:
    health = run_system_health_check()
    return {
        "status": health.get("overall_status", "warning"),
        "ok_count": health.get("ok_count", 0),
        "warning_count": health.get("warning_count", 0),
        "error_count": health.get("error_count", 0),
        "generated_at": health.get("generated_at"),
    }


def collect_database_health() -> dict:
    migration = initialize_database(database_config.DATABASE_URL)
    return {
        "status": "ok" if migration.get("status") == "ok" else "warning",
        "storage_enabled": bool(database_config.USE_DATABASE_STORAGE),
        "database_type": _database_type(database_config.DATABASE_URL),
        "tables_checked": migration.get("tables", 0),
        "warnings": [],
    }


def collect_security_health() -> dict:
    policy = get_security_policy().as_dict()
    return {
        "status": "ok" if not policy.get("warnings") else "warning",
        "auth_mode": policy.get("auth_mode"),
        "require_auth": policy.get("require_auth"),
        "allow_local_admin_fallback": policy.get("allow_local_admin_fallback"),
        "production_ready": policy.get("production_ready"),
        "warnings": policy.get("warnings", []),
    }


def collect_workspace_health() -> dict:
    repo = WorkspaceRepository(database_config.DATABASE_URL)
    default_workspace = repo.ensure_default_workspace("default")
    return {
        "status": "ok",
        "default_workspace_ready": bool(default_workspace),
        "workspace_isolation_enabled": True,
        "workspace_count": len(repo.list_workspaces_by_user("default")),
        "warnings": [],
    }


def collect_billing_health() -> dict:
    plan = get_workspace_plan("default", database_url=database_config.DATABASE_URL)
    quota = get_quota_status("default", database_url=database_config.DATABASE_URL)
    return {
        "status": "ok",
        "billing_mode": "mock",
        "real_payment_enabled": False,
        "plan": plan.get("plan_name", "free"),
        "quota_ready": bool(quota),
        "warnings": [],
    }


def collect_deployment_health() -> dict:
    startup = run_startup_check()
    return {
        "status": "ok" if startup.get("success") else "warning",
        "startup_check_success": bool(startup.get("success")),
        "check_count": len(startup.get("checks", [])),
        "warning_count": len(startup.get("warnings", [])),
        "error_count": len(startup.get("errors", [])),
    }


def collect_release_candidate_status() -> dict:
    document = PROJECT_ROOT / "docs" / "V2_RELEASE_CANDIDATE.md"
    return {
        "status": "ok" if document.exists() else "warning",
        "version": "V2.8",
        "v2_release_candidate_documented": document.exists(),
        "integration_check_available": (PROJECT_ROOT / "scripts" / "v2_integration_check.py").exists(),
        "freeze_status": "admin_console_added_after_v2_release_candidate",
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "warnings": [] if document.exists() else ["release candidate document missing"],
    }


def build_admin_console_summary() -> dict:
    warnings: list[str] = []
    sections = {
        "system": collect_system_health,
        "database": collect_database_health,
        "security": collect_security_health,
        "workspace": collect_workspace_health,
        "billing": collect_billing_health,
        "deployment": collect_deployment_health,
        "release_candidate": collect_release_candidate_status,
    }
    summary: dict[str, object] = {}
    for name, collector in sections.items():
        section, section_warnings = _safe_section(name, collector)
        summary[name] = section
        warnings.extend(section_warnings)
        warnings.extend(str(item) for item in section.get("warnings", []) if isinstance(section, dict))
    summary["warnings"] = warnings
    return _sanitize(summary)

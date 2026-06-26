from __future__ import annotations


def get_deployment_target_recommendation() -> dict:
    return {
        "frontend": "Vercel planned",
        "backend": "Render or Fly.io planned",
        "database": "PostgreSQL planned",
        "secrets": "managed secrets planned",
        "monitoring": "Sentry / OpenTelemetry planned",
    }


def get_deployment_target_checklist() -> list[str]:
    return [
        "choose frontend host",
        "choose backend host",
        "choose database provider",
        "choose protected config manager",
        "choose monitoring provider",
        "staging deployment first",
        "production launch approval",
    ]


def get_deployment_target_plan() -> dict:
    return {
        "current_state": "local_demo",
        "frontend_target": "vercel_planned",
        "backend_target": "render_or_flyio_planned",
        "database_target": "postgres_planned",
        "secrets_target": "secrets_manager_planned",
        "monitoring_target": "sentry_or_opentelemetry_planned",
        "production_deployment_enabled": False,
        "external_cloud_connected": False,
        "recommended_stack": get_deployment_target_recommendation(),
        "checklist": get_deployment_target_checklist(),
        "warnings": [],
    }


def validate_deployment_target_boundary() -> dict:
    return {
        "valid": True,
        "production_deployment_ready": False,
        "external_cloud_connected": False,
        "warnings": [],
    }
